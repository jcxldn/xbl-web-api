import os

from flask import Flask, jsonify, send_from_directory

import subprocess

import routes.profile
import routes.xuid
import routes.userstats

app = Flask(__name__, static_folder=None)


def get_client(main_xbl_client):
    global xbl_client
    xbl_client = main_xbl_client


def run_dev():
    port = os.getenv("PORT") or 3000
    app.run(host='0.0.0.0', port=port)


def res_as_json(data):
    return app.response_class(response=data, mimetype='application/json')

# Get the short SHA and return as string


def get_sha():
    return str(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()).split("'")[1::2][0]


def get_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)
    return routes


# add routes / blueprints from other files
app.register_blueprint(routes.profile.app, url_prefix="/profile")
app.register_blueprint(routes.xuid.app, url_prefix="/xuid")
app.register_blueprint(routes.userstats.app, url_prefix="/userstats")

# define routes
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/readme")
def readme():
    return send_from_directory("./", "README.md")


@app.route("/info")
def info():
    return jsonify({"sha": get_sha(), "routes": get_routes()})


@app.route("/titleinfo/<int:titleid>")
def titleinfo(titleid):
    return res_as_json(xbl_client.titlehub.get_title_info(titleid).content)


@app.route("/legacysearch/<query>")
def search360(query):
    return res_as_json(xbl_client.eds.get_singlemediagroup_search(query, 10, "Xbox360Game", domain="Xbox360").content)
