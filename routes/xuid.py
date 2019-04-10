from flask import Blueprint, jsonify

import json

import server

app = Blueprint('xuid', __name__)

def get_client(main_xbl_client):
    global xbl_client
    xbl_client = main_xbl_client

@app.route("/<gamertag>/raw")
def gamertag_to_xuid_raw(gamertag):
    return json.loads(xbl_client.profile.get_profile_by_gamertag(gamertag).content)["profileUsers"][0]["id"]


@app.route("/<gamertag>")
def gamertag_to_xuid(gamertag):
    return jsonify({"gamertag": gamertag, "xuid": gamertag_to_xuid_raw(gamertag)})
