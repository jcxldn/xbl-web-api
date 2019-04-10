from flask import Blueprint, jsonify

import json

import server

app = Blueprint(__name__.split(".")[1], __name__)

@app.route("/<gamertag>/raw")
def gamertag_to_xuid_raw(gamertag):
    return json.loads(server.xbl_client.profile.get_profile_by_gamertag(gamertag).content)["profileUsers"][0]["id"]


@app.route("/<gamertag>")
def gamertag_to_xuid(gamertag):
    return jsonify({"gamertag": gamertag, "xuid": gamertag_to_xuid_raw(gamertag)})
