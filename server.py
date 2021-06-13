# Flask-caching patch for quart
import quart.flask_patch
from quart import Quart, jsonify, send_from_directory, request

#from flask_cors import CORS

from cache import cache, add_cache_headers, default_secs
from cached_route import CachedRoute

import asyncio
import subprocess
import os

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
#
## Add timed reauth job
#@scheduler.task('interval', id='refresh_tokens', hours=1)
#def timed_reauth():
#    # This async function will refresh the tokens only *if* they are unavailable or expired
#    asyncio.run(xbl_client._auth_mgr.refresh_tokens())
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

q = QuartDecorator(app, loop)

@q.router("/titleinfo/<int:titleid>", 86400)
#@cr.jsonified_route("/titleinfo/<int:titleid>", 86400)
async def titleinfo(titleid):
    print("IN TITLEINFO")
    return (await xbl_client.titlehub.get_title_info(titleid)).json()


@cr.jsonified_route("/legacysearch/<query>", 86400)
def search360(query):
    return xbl_client.eds.get_singlemediagroup_search(query, 10, "Xbox360Game", domain="Xbox360").content


@cr.route("/gamertag/check/<gamertag>", 86400)
def gamertagcheck(gamertag):
    # See https://github.com/Prouser123/xbox-webapi-python/blob/master/xbox/webapi/api/provider/account.py
    code = xbl_client.account.claim_gamertag(1, gamertag).status_code
    return jsonify({"code": code, "available": "true" if code == 200 else "false"})



port = os.getenv("PORT") or 3000
app.run(host='0.0.0.0', port=port, loop=loop)
print("BRUH SESSION CLOSING")
session.close()