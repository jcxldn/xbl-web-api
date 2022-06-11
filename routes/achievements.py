from providers.BlueprintProvider import BlueprintProvider


class Achievements(BlueprintProvider):
    def routes(self):
        # ---------- Recent Achievements for user ----------
        @self.openXboxRoute("/1/recent/<int:xuid>")
        @self.validators.xuid()
        @self.pagedResponseModifier()
        async def recent1(xuid, continuationToken):
            return await self.xbl_client.achievements.get_achievements_xboxone_recent_progress_and_info(
                xuid, extra_params={"continuationToken": continuationToken}
            )

        @self.openXboxRoute(
            "/360/recent/<int:xuid>"
        )  # 500 when using continuationtoken
        @self.validators.xuid()
        async def recent360(xuid):
            return await self.xbl_client.achievements.get_achievements_xbox360_recent_progress_and_info(
                xuid
            )

        # ---------- Achievements for user & title ----------
        @self.openXboxRoute("/1/titleprogress/<int:xuid>/<int:titleid>")
        @self.validators.xuid()
        @self.pagedResponseModifier()
        async def titleprogress1(xuid, titleid, continuationToken):
            return await self.xbl_client.achievements.get_achievements_xboxone_gameprogress(
                xuid, titleid, extra_params={"continuationToken": continuationToken}
            )

        # Note that this endpoint displays all achievements as locked.
        @self.openXboxRoute("/360/titleprogress/all/<int:xuid>/<int:titleid>")
        @self.validators.xuid()
        @self.pagedResponseModifier()
        async def titleprogress360all(xuid, titleid, continuationToken):
            return await self.xbl_client.achievements.get_achievements_xbox360_all(
                xuid, titleid, extra_params={"continuationToken": continuationToken}
            )

        @self.openXboxRoute("/360/titleprogress/earned/<int:xuid>/<int:titleid>")
        @self.validators.xuid()
        @self.pagedResponseModifier()
        async def titleprogress360earned(xuid, titleid, continuationToken):
            return await self.xbl_client.achievements.get_achievements_xbox360_earned(
                xuid, titleid, extra_params={"continuationToken": continuationToken}
            )

        # ---------- Achievement details for user / scid / achievementID ----------
        @self.openXboxRoute(
            "/1/titleprogress/detail/<int:xuid>/<scid>/<int:achievementid>"
        )  # continuationToken does nothing (not required anyways? - only one achievement returned)
        @self.validators.xuid()
        async def titleprogress1detail(xuid, scid, achievementid):
            return await self.xbl_client.achievements.get_achievements_detail_item(
                xuid, scid, achievementid
            )
