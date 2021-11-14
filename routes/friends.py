from quart import jsonify

from providers.BlueprintProvider import BlueprintProvider


class Friends(BlueprintProvider):
    def __craftSummary(self, data):
        return jsonify(
            {
                "following": data.target_following_count,
                "followers": data.target_follower_count,
            }
        )

    def routes(self):
        @self.xbl_decorator.cachedRoute("/summary/xuid/<int:xuid>")
        async def xuid(xuid):
            return self.__craftSummary(
                await self.xbl_client.people.get_friends_summary_by_xuid(xuid)
            )

        @self.xbl_decorator.cachedRoute("/summary/gamertag/<gamertag>")
        async def gamertag(gamertag):
            return self.__craftSummary(
                await self.xbl_client.people.get_friends_summary_by_gamertag(gamertag)
            )
