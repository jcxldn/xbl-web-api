from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_apscheduler import APScheduler

from cache import cache, add_cache_headers, default_secs
from cached_route import CachedRoute

import subprocess
import os

import main
import routes.friends
import routes.profile
import routes.presence
import routes.xuid
import routes.userstats
import routes.usercolors
import routes.achievements
import routes.dev

app = Flask(__name__, static_folder=None)
# Get a CachedRoute instance for routes defined in this file
cr = CachedRoute(app)

# Init scheduler
scheduler = APScheduler()
# Set option
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

# Init caching
cache.init_app(app)
cache.clear()

# Add timed reauth job
@scheduler.task('interval', id='do_timed_reauth_hourly', hours=1)
def timed_reauth():
    print('[Timed ReAuth] Authenticated: ' + str(main.auth_mgr.authenticated))
    if not main.auth_mgr.authenticated:
        print('[Timed ReAuth] Not authenticated, authenticating!')
        main.authenticate()

@scheduler.task('interval', id='hello_60s', seconds=60)
def hello60():
    print("Hello 60s!")

# Setup CORS
CORS(app)

# Setup after_request to add caching headers
@app.after_request
def after_request(res):
    res.direct_passthrough = False  # https://github.com/pallets/flask/issues/993
    res.add_etag()
    res.make_conditional(request) # unsure if required
    res.cache_control.max_age = default_secs
    res.cache_control.public = True
    return res

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
app.register_blueprint(routes.friends.app, url_prefix="/friends")
app.register_blueprint(routes.profile.app, url_prefix="/profile")
app.register_blueprint(routes.presence.app, url_prefix="/presence")
app.register_blueprint(routes.xuid.app, url_prefix="/xuid")
app.register_blueprint(routes.userstats.app, url_prefix="/userstats")
app.register_blueprint(routes.usercolors.app, url_prefix="/usercolors")
app.register_blueprint(routes.achievements.app, url_prefix="/achievements")
app.register_blueprint(routes.dev.app, url_prefix="/dev")

# define routes
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/readme")
def readme():
    return send_from_directory("./", "README.md")


@cr.route("/info")
def info():
    return jsonify({"sha": get_sha(), "routes": get_routes()})


@cr.jsonified_route("/titleinfo/<int:titleid>")
def titleinfo(titleid):
    return xbl_client.titlehub.get_title_info(titleid).content


@cr.jsonified_route("/legacysearch/<query>")
def search360(query):
    return xbl_client.eds.get_singlemediagroup_search(query, 10, "Xbox360Game", domain="Xbox360").content


@cr.route("/gamertag/check/<gamertag>")
def gamertagcheck(gamertag):
    # See https://github.com/Prouser123/xbox-webapi-python/blob/master/xbox/webapi/api/provider/account.py
    code = xbl_client.account.claim_gamertag(1, gamertag).status_code
    return jsonify({"code": code, "available": "true" if code == 200 else "false"})
