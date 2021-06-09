from flask import Blueprint

import server
import routes.xuid

from cached_route import CachedRoute

app = Blueprint(__name__.split(".")[1], __name__)
cr = CachedRoute(app)

@cr.jsonified_route("/xuid/<int:xuid>/titleid/<int:titleid>")
def xuidTitleIdStats(xuid, titleid):
    return server.xbl_client.userstats.get_stats_batch([xuid], titleid).content

# Not using jsonified_route as xuidTitleIdStats already uses it
@cr.route("/gamertag/<gamertag>/titleid/<int:titleid>")
def gamertagTitleIdStats(gamertag, titleid):
    return xuidTitleIdStats(routes.xuid.gamertag_to_xuid_raw(gamertag), titleid)