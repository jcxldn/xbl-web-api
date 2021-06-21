# Flask-caching patch for quart
import quart.flask_patch
from quart import Quart, jsonify, send_from_directory, request

# Hypercorn (Quart ASGI webserver)
from hypercorn.config import Config
from hypercorn.asyncio import serve

from apscheduler.schedulers.asyncio import AsyncIOScheduler

#from flask_cors import CORS

from cache import cache, add_cache_headers, default_secs
from cached_route import CachedRoute

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

loop = asyncio.get_event_loop()
print("USING LOOP")
print(loop)
app = Quart(__name__, static_folder=None)
# auth me uwu
xbl_client, session = loop.run_until_complete(main.authenticate(loop))

# Setup & start the scheduler
scheduler = AsyncIOScheduler(event_loop=loop)
scheduler.start()
# Get a CachedRoute instance for routes defined in this file
cr = CachedRoute(app, loop)

# Init scheduler
#scheduler = APScheduler()
# Set options
#scheduler.api_enabled = False
#scheduler.init_app(app)
#scheduler.start()

# Init caching
cache.init_app(app)
cache.clear()

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

#
#@scheduler.task('interval', id='hello_60s', seconds=60)
#def hello60():
#    print("Hello 60s!")
#
# Setup CORS
#CORS(app)

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
@cr.route("/info", 86400)
#@app.route("/info")
#@cache.cached(300)
def info():
    return jsonify({"sha": get_sha(), "routes": get_routes()})


from providers.QuartDecoratorProvider import QuartDecorator
from providers.XblDecoratorProvider import XblDecorator

q = QuartDecorator(app, loop)
x = XblDecorator(app, loop)

@x.openXboxRoute("/titleinfo/<int:titleid>", 86400)
#@cr.jsonified_route("/titleinfo/<int:titleid>", 86400)
async def titleinfo(titleid):
    print("IN TITLEINFO")
    return await xbl_client.titlehub.get_title_info(titleid)


# legacysearch (EDS) has been removed from xbox-webapi v2
# Return a 410 (Gone) here?
#@x.openXboxRoute("/legacysearch/<query>", 86400)
#async def search360(query):
#    return xbl_client.eds.get_singlemediagroup_search(query, 10, "Xbox360Game", domain="Xbox360").content


@x.router("/gamertag/check/<gamertag>", 86400)
async def gamertagcheck(gamertag):
    # Use .value to get the int instead of the enum
    code = (await xbl_client.account.claim_gamertag(1, gamertag)).value
    return jsonify({"available": "true" if code == 200 else "false" if code == 409 else "unknown" })


# Create hypercorn config object
port = os.getenv("PORT") or 3000
config = Config()
config.bind = ["0.0.0.0:%i" % port]

# Run hypercorn in the same loop as xbl_client
loop.run_until_complete(serve(app, config))

# When we get here, hypercorn has finished so we can just close the ClientSession
print("Serve future done!")
loop.run_until_complete(session.close())