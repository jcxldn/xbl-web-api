from flask import Blueprint

import server
import routes.xuid

app = Blueprint(__name__.split(".")[1], __name__)

@app.route("/xuid/<int:xuid>/titleid/<int:titleid>")
def xuidTitleIdStats(xuid, titleid):
    return server.res_as_json(server.xbl_client.userstats.get_stats_batch([xuid], titleid).content)

@app.route("/gamertag/<gamertag>/titleid/<int:titleid>")
def gamertagTitleIdStats(gamertag, titleid):
    return xuidTitleIdStats(routes.xuid.gamertag_to_xuid_raw(gamertag), titleid)