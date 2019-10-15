from flask import Blueprint, jsonify
import json

import server
import routes.xuid

app = Blueprint(__name__.split(".")[1], __name__)


def getSinglePresence(xuid):
    return server.xbl_client.presence.get_presence(str(xuid)).content


@app.route("/xuid/<int:xuid>")
def xuid(xuid):
    return server.res_as_json(getSinglePresence(xuid))


@app.route("/gamertag/<gamertag>")
def gamertag(gamertag):
    # Get the data from the client as a python JSON object
    data = json.loads(getSinglePresence(
        routes.xuid.gamertag_to_xuid_raw(gamertag)))
    # Add the gamertag to the JSON response
    data["gamertag"] = gamertag

    # Dump (stringify) the data and send it as the response
    return server.res_as_json(json.dumps(data))
