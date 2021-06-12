from flask import Blueprint, jsonify
import json

import server

from cached_route import CachedRoute

app = Blueprint(__name__.split(".")[1], __name__)
cr = CachedRoute(app)


def craftSummary(data):
    return json.dumps({"following": data["targetFollowingCount"], "followers": data["targetFollowerCount"]})


@cr.jsonified_route("/summary/xuid/<int:xuid>")
def xuid(xuid):
    data = json.loads(
        server.xbl_client.people.get_friends_summary_by_xuid(xuid).content)
    return craftSummary(data)


@cr.jsonified_route("/summary/gamertag/<gamertag>")
def gamertag(gamertag):
    data = json.loads(
        server.xbl_client.people.get_friends_summary_by_gamertag(gamertag).content)
    return craftSummary(data)
