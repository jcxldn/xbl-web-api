from flask import Blueprint, jsonify
import json

import server
import routes.xuid

from cached_route import CachedRoute

app = Blueprint(__name__.split(".")[1], __name__)
cr = CachedRoute(app)

def getSinglePresence(xuid):
    return server.xbl_client.presence.get_presence(str(xuid)).content


@cr.route("/xuid/<int:xuid>")
def xuid(xuid):
    print("uwu")
    return server.res_as_json(getSinglePresence(xuid))


@cr.route("/gamertag/<gamertag>")
def gamertag(gamertag):
    # Get the data from the client as a python JSON object
    data = json.loads(getSinglePresence(
        routes.xuid.gamertag_to_xuid_raw(gamertag)))
    # Add the gamertag to the JSON response
    data["gamertag"] = gamertag

    # Dump (stringify) the data and send it as the response
    return server.res_as_json(json.dumps(data))
