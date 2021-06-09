from flask import Blueprint, jsonify

import json

import server

from cached_route import CachedRoute

app = Blueprint(__name__.split(".")[1], __name__)
cr = CachedRoute(app)

# ---------- Recent Achievements for user ----------


@cr.jsonified_route("/1/recent/<int:xuid>")
def recent1(xuid):
    return server.xbl_client.achievements.get_achievements_xboxone_recent_progress_and_info(xuid)


@cr.jsonified_route("/360/recent/<int:xuid>")
def recent360(xuid):
    return server.xbl_client.achievements.get_achievements_xbox360_recent_progress_and_info(xuid)

# ---------- Achievements for user & title ----------

@cr.jsonified_route("/1/titleprogress/<int:xuid>/<int:titleid>")
def titleprogress1(xuid, titleid):
    return server.xbl_client.achievements.get_achievements_xboxone_gameprogress(xuid, titleid)


# Note that this endpoint displays all achievements as locked.
@cr.jsonified_route("/360/titleprogress/all/<int:xuid>/<int:titleid>")
def titleprogress360all(xuid, titleid):
    return server.xbl_client.achievements.get_achievements_xbox360_all(xuid, titleid)


@cr.jsonified_route("/360/titleprogress/earned/<int:xuid>/<int:titleid>")
def titleprogress360earned(xuid, titleid):
    return server.xbl_client.achievements.get_achievements_xbox360_earned(xuid, titleid)

# ---------- Achievement details for user / scid / achievementID ----------

@cr.jsonified_route("/1/titleprogress/detail/<int:xuid>/<scid>/<int:achievementid>")
def titleprogress1detail(xuid, scid, achievementid):
    return server.xbl_client.achievements.get_achievements_detail_item(xuid, scid, achievementid)
