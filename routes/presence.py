from aiohttp import ClientResponse
from quart import jsonify

from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider


class Presence(BlueprintProvider, LoopbackRequestProvider):
    def routes(self):
        @self.openXboxRoute("/xuid/<int:xuid>")
        @self.validators.xuid()
        async def xuid(xuid):
            # Currently getSinglePresence is not part of any release
            # return await self.xbl_client.presence.get_presence(str(xuid))

            return (await self.xbl_client.presence.get_presence_batch([str(xuid)]))[0]

        @self.openXboxRoute("/gamertag/<gamertag>")
        @self.validators.gamertag()
        async def gamertag(gamertag):
            # 1. Get the XUID for this user
            #    This is *not* a good way to call other routes (you should just call the function directly)
            #    ALSO SEE: xuid.py#L34
            #    but it does mean we cache our results! :upside_down_face:

            # This is a callback for after the localhost request has been made.
            async def on_finish(res: ClientResponse):
                # Check status code
                # (If we get here we already have a response object so no need to check for that)
                if res.status == 200:
                    xuid = str((await res.json())["xuid"])
                    print("Got XUID: %s" % xuid)

                    # Now we're gonna do the same thing but with /presence/xuid
                    # This function serves as a callback after we look up the presence via XUID.
                    async def on_presence_lookup_finish(presenceRes: ClientResponse):
                        return jsonify(await presenceRes.json())

                    # Get presence via xuid, using above function as a callback
                    # As below, the callback will return a response so we can just return the output once awaited
                    return await self.get(
                        "http://localhost:%i/presence/xuid/%s"
                        % (self.xbl_client._xbl_web_api_current_port, xuid),
                        on_presence_lookup_finish,
                    )

                else:
                    # Passthough response content (handled in above route)
                    response = jsonify(await res.json())
                    response.status_code = 404
                    return response

            # Make a async request to our own xuid endpoint, awaiting on_finish as a callback
            # on_finish will return our crafted response, so we can return the output once awaited
            return await self.get(
                "http://localhost:%i/xuid/%s"
                % (self.xbl_client._xbl_web_api_current_port, gamertag),
                on_finish,
            )
