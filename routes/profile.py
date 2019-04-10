from flask import Blueprint
import sys

import server
import routes.xuid

app = Blueprint('profile', __name__)

def get_client(main_xbl_client):
    global xbl_client
    xbl_client = main_xbl_client


# Profile Settings Routes (these don't have as much info)


@app.route("/settings/gamertag/<gamertag>")
def settings_gamertag(gamertag):
    return server.res_as_json(xbl_client.profile.get_profile_by_gamertag(gamertag).content)


@app.route("/settings/xuid/<int:xuid>")
def settings_xuid(xuid):
    return server.res_as_json(xbl_client.profile.get_profile_by_xuid(xuid).content)


# Profile Routes

@app.route("/xuid/<int:xuid>")
def xuid(xuid):
    return server.res_as_json(xbl_client.profile.get_profiles([xuid]).content)


@app.route("/gamertag/<gamertag>")
def gamertag(gamertag):
    return xuid(routes.xuid.gamertag_to_xuid_raw(gamertag))
