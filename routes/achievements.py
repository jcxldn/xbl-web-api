from flask import Blueprint, jsonify

import json

import server

app = Blueprint(__name__.split(".")[1], __name__)

# ---------- Recent Achievements for user ----------


@app.route("/1/recent/<int:xuid>")
def recent1(xuid):
    return server.res_as_json(server.xbl_client.achievements.get_achievements_xboxone_recent_progress_and_info(xuid))


@app.route("/360/recent/<int:xuid>")
def recent360(xuid):
    return server.res_as_json(server.xbl_client.achievements.get_achievements_xbox360_recent_progress_and_info(xuid))

# ---------- Achievements for user & title ----------

@app.route("/1/titleprogress/<int:xuid>/<int:titleid>")
def titleprogress1(xuid, titleid):
    return server.res_as_json(server.xbl_client.achievements.get_achievements_xboxone_gameprogress(xuid, titleid))


# Note that this endpoint displays all achievements as locked.
@app.route("/360/titleprogress/all/<int:xuid>/<int:titleid>")
def titleprogress360all(xuid, titleid):
    return server.res_as_json(server.xbl_client.achievements.get_achievements_xbox360_all(xuid, titleid)).heade


@app.route("/360/titleprogress/earned/<int:xuid>/<int:titleid>")
def titleprogress360earned(xuid, titleid):
    return server.res_as_json(server.xbl_client.achievements.get_achievements_xbox360_earned(xuid, titleid))

# ---------- Achievement details for user / scid / achievementID ----------

@app.route("/1/titleprogress/detail/<int:xuid>/<scid>/<int:achievementid>")
def titleprogress1detail(xuid, scid, achievementid):
    return server.res_as_json(server.xbl_client.achievements.get_achievements_detail_item(xuid, scid, achievementid))
