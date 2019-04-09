import os
import json

from flask import Flask, jsonify

app = Flask(__name__, static_folder=None)


def get_client(main_xbl_client):
    global xbl_client
    xbl_client = main_xbl_client


def run_dev():
    port = os.getenv("PORT") or 3000
    app.run(host='0.0.0.0', port=port)


def res_as_json(data):
    return app.response_class(response=data, mimetype='application/json')


# define routes
@app.route("/")
def hello():
    return jsonify({"hello": "hello, world!"})


@app.route("/routes")
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)
    return jsonify(routes)


@app.route("/xuid/<gamertag>/raw")
def gamertag_to_xuid_raw(gamertag):
    return json.loads(xbl_client.profile.get_profile_by_gamertag(gamertag).content)["profileUsers"][0]["id"]


@app.route("/xuid/<gamertag>")
def gamertag_to_xuid(gamertag):
    return jsonify({"gamertag": gamertag, "xuid": gamertag_to_xuid_raw(gamertag)})


@app.route("/profile/settings/gamertag/<gamertag>")
def profilesettings_gamertag(gamertag):
    return res_as_json(xbl_client.profile.get_profile_by_gamertag(gamertag).content)


@app.route("/profile/settings/xuid/<int:xuid>")
def profilesettings_xuid(xuid):
    return res_as_json(xbl_client.profile.get_profile_by_xuid(xuid).content)


@app.route("/profile/xuid/<int:xuid>")
def profile_xuid(xuid):
    return res_as_json(xbl_client.profile.get_profiles([xuid]).content)


@app.route("/profile/gamertag/<gamertag>")
def profile_gamertag(gamertag):
    return profile_xuid(gamertag_to_xuid_raw(gamertag))
