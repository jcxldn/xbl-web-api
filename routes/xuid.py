from flask import Blueprint, jsonify

import json

import server

app = Blueprint(__name__.split(".")[1], __name__)


def isInt(value):
    try:
        value = int(value)
        return True
    except (ValueError, TypeError):
        # pass  # it was a string, not an int.
        return False


@app.route("/<gamertag>/raw")
def gamertag_to_xuid_raw(gamertag):
    # make the request
    req = server.xbl_client.profile.get_profile_by_gamertag(gamertag)
    # if there were any errors, return the error code
    if (req.status_code != 200):
        message = "not found" if req.status_code == 404 else ""
        return jsonify({"error": req.status_code, "message": message, "gamertag": gamertag}), req.status_code
    # if there were no errors, return the bit of the response we want
    return json.loads(req.content)["profileUsers"][0]["id"]


@app.route("/<gamertag>")
def gamertag_to_xuid(gamertag):
    # make the request
    req = gamertag_to_xuid_raw(gamertag)
    # if an error was recieved, return the error
    if (not isInt(req)):
        return req
    # if there were no errors, return the usual response
    return jsonify({"gamertag": gamertag, "xuid": gamertag_to_xuid_raw(gamertag)})
