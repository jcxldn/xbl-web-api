from flask import Blueprint, jsonify
import json

import server

app = Blueprint(__name__.split(".")[1], __name__)


def craftSummaryResponse(data):
    return server.res_as_json(json.dumps({"following": data["targetFollowingCount"], "followers": data["targetFollowerCount"]}))


@app.route("/summary/xuid/<int:xuid>")
def xuid(xuid):
    data = json.loads(
        server.xbl_client.people.get_friends_summary_by_xuid(xuid).content)
    return craftSummaryResponse(data)


@app.route("/summary/gamertag/<gamertag>")
def gamertag(gamertag):
    data = json.loads(
        server.xbl_client.people.get_friends_summary_by_gamertag(gamertag).content)
    return craftSummaryResponse(data)
