from quart import jsonify

from providers.BlueprintProvider import BlueprintProvider


class Dev(BlueprintProvider):
    def routes(self):
        @self.xbl_decorator.router("/reauth")
        async def reauth():
            await self.xbl_client._auth_mgr.refresh_tokens()
            return jsonify({"message": "success"})

        @self.xbl_decorator.router("/isauth")
        async def isauth():
            oauth = self.xbl_client._auth_mgr.oauth.is_valid()
            user = self.xbl_client._auth_mgr.user_token.is_valid()
            xsts = self.xbl_client._auth_mgr.xsts_token.is_valid()
            return jsonify(
                {
                    "authenticated": oauth and user and xsts,
                }
            )
