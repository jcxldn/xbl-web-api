from aiohttp import ClientResponse
from quart import jsonify

from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider

class Presence(BlueprintProvider, LoopbackRequestProvider):
    async def getSinglePresence(self, xuid):
        # Currently getSinglePresence is not part of any release
        #return await self.xbl_client.presence.get_presence(str(xuid))

        return (await self.xbl_client.presence.get_presence_batch([str(xuid)]))[0]
    
    def routes(self):
        @self.openXboxRoute("/xuid/<int:xuid>")
        async def xuid(xuid):
            return await self.getSinglePresence(xuid)

        @self.openXboxRoute("/gamertag/<gamertag>")
        async def gamertag(gamertag):
            # 1. Get the XUID for this user
            #    This is *not* a good way to call other routes (you should just call the function directly)
            #    ALSO SEE: xuid.py#L34
            #    but it does mean we cache our results! :upside_down_face:
            
            # This is a callback for after the localhost request has been made.
            async def on_finish(res: ClientResponse):
                # 1. Check status code
                # (If we get here we already have a response object so no need to check for that)
                if (res.status == 200):
                    xuid = str((await res.json())["xuid"])
                    print("Got XUID: %s" % xuid)
                    # Now that we have the xuid (albeit with a bad method) we can call getSinglePresence as before
                    # TODO: caching method for this as well?
                    return await self.getSinglePresence(xuid)
                else:
                    # Passthough response content (handled in above route)
                    response = jsonify(await res.json())
                    response.status_code = 404
                    return response

            # Make a async request to our own xuid endpoint, awaiting on_finish as a callback
            # on_finish will return our crafted response, so we can return the output once awaited
            return await self.get("http://localhost:%i/xuid/%s" % (self.xbl_client._xbl_web_api_current_port, gamertag), on_finish)