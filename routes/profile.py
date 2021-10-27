from aiohttp import ClientResponse
from quart import jsonify

from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider

class Profile(BlueprintProvider, LoopbackRequestProvider):
    def routes(self):
        # ---------- Profile Settings Routes (these don't have as much info) ----------
        @self.openXboxRoute("/settings/gamertag/<gamertag>")
        async def settings_gamertag(gamertag):
            return await self.xbl_client.profile.get_profile_by_gamertag(gamertag)
        
        @self.openXboxRoute("/settings/xuid/<int:xuid>")
        async def settings_xuid(xuid):
            return await self.xbl_client.profile.get_profile_by_xuid(xuid)

        # ---------- Profile Routes ----------
        @self.openXboxRoute("/xuid/<int:xuid>")
        async def xuid(xuid):
            # TODO: skipping XUID validation for now, will do for all routes afterwards
            # Assume xuid is valid
            return await self.xbl_client.profile.get_profiles([xuid])


        @self.openXboxRoute("/gamertag/<gamertag>")
        async def gamertag(gamertag):
            # 1. Convert gamertag to XUID
            # Making local http requests so we can grab cached data,
            # minimizing the amountt of calls made to Xbox Live.
            # See xuid.py#L34

            async def on_finish(res: ClientResponse):
            # We know the type already, just check the status code
                if (res.status == 200):
                    xuid = str((await res.json())["xuid"])
                    print("Got XUID: %s" % xuid)
                    # 2. Lookup profile via xuid (using local http requests to take advantage of cached data)

                    # Now we're gonna do this again but for /profile/xuid
                    # The callback will return a response so we can just return the output once awaited
                    async def on_profile_lookup_finish(profileRes: ClientResponse):
                        return jsonify(await profileRes.json())
                    
                    # Get profile via xuid, using above function as a callback
                    # As below, the callback will return a response so we can just return the output once awaited
                    return await self.get("http://localhost:%i/profile/xuid/%s" % (self.xbl_client._xbl_web_api_current_port, xuid), on_profile_lookup_finish)
                else:
                    # Passthough response content (handled in above route)
                    response = jsonify(await res.json())
                    response.status_code = 404
                    return response
            
            # Make a async request to our own xuid endpoint, awaiting on_finish as a callback
            # on_finish will return our crafted response, so we can return the output once awaited
            return await self.get("http://localhost:%i/xuid/%s" % (self.xbl_client._xbl_web_api_current_port, gamertag), on_finish)