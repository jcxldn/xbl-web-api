from flask import Blueprint, jsonify

import json

from quart import request

#import server

from cached_route import CachedRoute


from providers.BlueprintProvider import BlueprintProvider


def tryParseInt(val, fallback):
    if val.isdigit():
        return int(val)
    else:
        return fallback

class Achievements(BlueprintProvider):
    def routes(self):
        # ---------- Recent Achievements for user ----------
        @self.openXboxRoute("/1/recent/<int:xuid>")
        async def recent1(xuid):
            return await self.xbl_client.achievements.get_achievements_xboxone_recent_progress_and_info(xuid)
        
        @self.openXboxRoute("/360/recent/<int:xuid>")
        async def recent360(xuid):
            return await self.xbl_client.achievements.get_achievements_xbox360_recent_progress_and_info(xuid)

        # ---------- Achievements for user & title ----------
        # gay: continuationToken
        @self.openXboxRoute("/1/titleprogress/<int:xuid>/<int:titleid>")
        async def titleprogress1(xuid, titleid):
            continuationToken = tryParseInt(request.args.get("continuationToken"), 0)
            print("Found continuationToken: '%s'" % str(continuationToken))

            return await self.xbl_client.achievements.get_achievements_xboxone_gameprogress(xuid, titleid, extra_params = {"continuationToken": continuationToken })

        # Note that this endpoint displays all achievements as locked.
        @self.openXboxRoute("/360/titleprogress/all/<int:xuid>/<int:titleid>")
        async def titleprogress360all(xuid, titleid):
            return await self.xbl_client.achivements.get_achivements_xbox360_all(xuid, titleid)

        @self.openXboxRoute("/360/titleprogress/earned/<int:xuid>/<int:titleid>")
        async def titleprogress360earned(xuid, titleid):
            return await self.xbl_client.achivements.get_achivements_xbox360_earned(xuid, titleid)

        # ---------- Achievement details for user / scid / achievementID ----------
        @self.openXboxRoute("/1/titleprogress/detail/<int:xuid>/<scid>/<int:achievementid>")
        async def titleprogress1detail(xuid, scid, achievementid):
            return await self.xbl_client.achievements.get_achievements_detail_item(xuid, scid, achievementid)