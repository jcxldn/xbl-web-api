from flask import Blueprint, jsonify

import server
import routes.xuid

from cached_route import CachedRoute

app = Blueprint(__name__.split(".")[1], __name__)
cr = CachedRoute(app)


# Profile Settings Routes (these don't have as much info)


@cr.jsonified_route("/settings/gamertag/<gamertag>")
def settings_gamertag(gamertag):
    return server.xbl_client.profile.get_profile_by_gamertag(gamertag).content


@cr.jsonified_route("/settings/xuid/<int:xuid>")
def settings_xuid(xuid):
    return server.xbl_client.profile.get_profile_by_xuid(xuid).content


# Profile Routes

@cr.jsonified_route("/xuid/<int:xuid>")
def xuid(xuid):
    # Check if the XUID is valid, and if not, return an error
    if (not routes.xuid.isXUID(xuid)):
        return jsonify({"error": 400, "message": "invalid xuid"}), 400
    # if the xuid is valid, make the API request
    req = server.xbl_client.profile.get_profiles([xuid])
    # Client returns code 400 instead of 404
    if (req.status_code == 400):
        return jsonify({"error": 404, "message": "user not found"}), 404
    # return the usual response if there were no issues
    return req.content


# Not using jsonified_route as xuid is already using it
@cr.route("/gamertag/<gamertag>")
def gamertag(gamertag):
    # make the request
    req = routes.xuid.gamertag_to_xuid_raw(gamertag)
    # if an error was recieved (it will return an object), return the error
    if (not routes.xuid.isInt(req)):
        return req
    # if there were no errors, return the usual response
    return xuid(req)
