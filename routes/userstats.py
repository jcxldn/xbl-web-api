from quart import jsonify
from aiohttp import ClientResponse
from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider

import json


class Userstats(BlueprintProvider, LoopbackRequestProvider):
    def routes(self):
        @self.openXboxRoute("/xuid/<int:xuid>/titleid/<int:titleid>")
        async def xuidTitleIdStats(xuid, titleid):
            return await self.xbl_client.userstats.get_stats_batch([xuid], titleid)

        @self.xbl_decorator.cachedRoute("/gamertag/<gamertag>/titleid/<int:titleid>")
        async def gamertagTitleIdStats(gamertag, titleid):
            # 1. Get xuid from gamertag - See: xuid.py#L34
            async def on_xuid_lookup_finish(xuidRes: ClientResponse):
                # Check status code
                if xuidRes.status == 200:
                    # Get the response body
                    body = await xuidRes.text()
                    # Parse as JSON
                    data = json.loads(body)
                    # Get the xuid string from the json object
                    xuid = data["xuid"]

                    # 2. Call xuidTitleIdStats (seen above) with our xuid
                    async def on_stats_request_finish(statsRes: ClientResponse):
                        if statsRes.status == 200:
                            # Return the result we recieved as a response
                            response = jsonify(await statsRes.json())
                            response.headers.add_header(
                                "x-upstream-queried-at",
                                statsRes.headers.get("x-queried-at"),
                            )
                            return response
                        else:
                            response = jsonify(
                                {
                                    "error": "error getting stats",
                                    "code": statsRes.status,
                                }
                            )
                            response.status_code = 404
                            return response

                    # Make an async request to our own xuid titleid stats endpoint using a callback
                    return await self.get(
                        "http://localhost:%i/userstats/xuid/%s/titleid/%s"
                        % (self.xbl_client._xbl_web_api_current_port, xuid, titleid),
                        on_stats_request_finish,
                    )
                # on_xuid_lookup_finish -> status code is not 404
                else:
                    response = jsonify(
                        {"error": "could not resolve gamertag", "code": xuidRes.status}
                    )
                    response.status_code = 404
                    return response

            # Make a async request to our own xuid endpoint, using on_xuid_lookup_finish as a callback
            # Return whatever was returned (eg. a Response object)
            return await self.get(
                "http://localhost:%i/xuid/%s"
                % (self.xbl_client._xbl_web_api_current_port, gamertag),
                on_xuid_lookup_finish,
            )
