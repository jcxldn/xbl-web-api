# Flask-caching patch for quart
import quart.flask_patch
from quart import Quart, jsonify, send_from_directory, request

# Hypercorn (Quart ASGI webserver)
from hypercorn.config import Config
from hypercorn.asyncio import serve

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from providers import LoggingProvider

#from flask_cors import CORS

import asyncio
import subprocess
import os
import logging

import main
#import routes.friends
#import routes.profile
#import routes.presence
#import routes.xuid
#import routes.userstats
#import routes.usercolors
#import routes.achievements
#import routes.dev

logger = LoggingProvider.getLogger("server")

loop = asyncio.get_event_loop()
logger.info("Using loop: %s" % str(loop))
app = Quart(__name__, static_folder=None)
xbl_client, session = loop.run_until_complete(main.authenticate(loop))

# Get a cacheprovider
from providers.caching.DiskCacheProvider import DiskCacheProvider
cache = DiskCacheProvider("/tmp/xbl-web-api")

# Setup & start the scheduler
scheduler = AsyncIOScheduler(event_loop=loop)
scheduler.start()

# Define scheduled tasks
sched_logger = logging.getLogger("sched.timed_reauth")
@scheduler.scheduled_job('interval', minutes=1)
async def job_timed_reauth():
    is_same_loop = asyncio.get_running_loop() is loop
    if (is_same_loop):
        sched_logger.debug("In the same event loop! Refreshing tokens if needed...")
        # This async function will refresh the tokens only *if* they are unavailable or expired
        await xbl_client._auth_mgr.refresh_tokens()
    else:
        sched_logger.error("Not in the same event loop!")
        raise RuntimeError("Timed Reauth not in same loop!")

@scheduler.scheduled_job('interval', minutes=5)
async def job_cache_cleanup():
    # This job will remove expired items from the cache
    number_removed = cache.remove_expired()

    # Get a logger and print details on how much we cleared
    logger = logging.getLogger("sched.cache_cleanup")
    logger.info("Removed %i expired items from cache." % number_removed)
    logger.info("New cache size is %i items." % cache.len())

# Setup after_request to add caching headers

def get_client(main_xbl_client):
    global xbl_client
    xbl_client = main_xbl_client


# Get the short SHA and return as string
def get_sha():
    if 'GIT_COMMIT' in os.environ:
        return os.getenv('GIT_COMMIT')[0:7]
    else:
        return str(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()).split("'")[1::2][0]


def get_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)
    return routes


from routes.achievements import Achievements
app.register_blueprint(Achievements(loop, xbl_client, cache).app, url_prefix="/achievements")

from routes.dev import Dev
app.register_blueprint(Dev(loop, xbl_client, cache).app, url_prefix="/dev")

from routes.friends import Friends
app.register_blueprint(Friends(loop, xbl_client, cache).app, url_prefix="/friends")

from routes.presence import Presence
app.register_blueprint(Presence(loop, xbl_client, cache).app, url_prefix="/presence")

from routes.profile import Profile
app.register_blueprint(Profile(loop, xbl_client, cache).app, url_prefix="/profile")

from routes.xuid import Xuid
app.register_blueprint(Xuid(loop, xbl_client, cache).app, url_prefix="/xuid")

# add routes / blueprints from other files
#app.register_blueprint(routes.friends.app, url_prefix="/friends")
#app.register_blueprint(routes.profile.app, url_prefix="/profile")
#app.register_blueprint(routes.presence.app, url_prefix="/presence")
#app.register_blueprint(routes.xuid.app, url_prefix="/xuid")
#app.register_blueprint(routes.userstats.app, url_prefix="/userstats")
#app.register_blueprint(routes.usercolors.app, url_prefix="/usercolors")
#app.register_blueprint(routes.achievements.app, url_prefix="/achievements")
#app.register_blueprint(routes.dev.app, url_prefix="/dev")

# define routes
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/readme")
def readme():
    return send_from_directory("./", "README.md")


# Note: 1 day cache (86400s) on following routes
#@cr.route("/info", 86400)
@app.route("/info")
#@cache.cached(300)
def info():
    return jsonify({"sha": get_sha(), "routes": get_routes()})


from providers.XblDecoratorProvider import XblDecorator

# Init XblDecorator (inherits from QuartDecorator)
router = XblDecorator(app, loop, cache)

@router.openXboxRoute("/titleinfo/<int:titleid>", 86400)
#@cr.jsonified_route("/titleinfo/<int:titleid>", 86400)
async def titleinfo(titleid):
    return await xbl_client.titlehub.get_title_info(titleid)


# legacysearch (EDS) has been removed from xbox-webapi v2
# Return a 410 (Gone) here?
#@x.openXboxRoute("/legacysearch/<query>", 86400)
#async def search360(query):
#    return xbl_client.eds.get_singlemediagroup_search(query, 10, "Xbox360Game", domain="Xbox360").content


@router.cachedRoute("/gamertag/check/<gamertag>", 86400)
async def gamertagcheck(gamertag):
    # Use .value to get the int instead of the enum
    code = (await xbl_client.account.claim_gamertag(1, gamertag)).value
    return jsonify({"available": "true" if code == 200 else "false" if code == 409 else "unknown" })


# Create hypercorn config object
port = os.getenv("PORT") or 3000
config = Config()
config.bind = ["0.0.0.0:%i" % port]

# Save the port so we can access it later
# Making loopback requests is a *bad* idea but we do get cached results this way!
xbl_client._xbl_web_api_current_port = port

# Run hypercorn in the same loop as xbl_client
loop.run_until_complete(serve(app, config))

# When we get here, hypercorn has finished so we can just close the ClientSession
logger.info("Serve future done! Closing session...")
loop.run_until_complete(session.close())