from aiohttp import ClientResponse
from quart import Response, render_template, jsonify

import json

from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider


class Usercolors(BlueprintProvider, LoopbackRequestProvider):
    async def createUsercolorsResponse(self, primary, secondary, tertiary, *headers):
        r = await render_template(
            "usercolors.esvg", primary=primary, secondary=secondary, tertiary=tertiary
        )
        print(type(r))
        return Response(r, mimetype="image/svg+xml", headers=headers)

    def routes(self):
        @self.xbl_decorator.cachedRoute("/define/<primary>/<secondary>/<tertiary>")
        async def define(primary, secondary, tertiary):
            return await self.createUsercolorsResponse(
                primary, secondary, tertiary, ["X-XBL-WEB-API-Colors-Source", "defined"]
            )

        @self.xbl_decorator.cachedRoute("/get/xuid/<int:xuid>")
        async def getXuid(xuid):
            # 1. Get profile data (/profile/gamertag/)
            #    See: xuid.py#L34

            # This is a callback for after the localhost request has been made.
            async def on_finish(res: ClientResponse):
                # Check status code
                # (If we get here we already have a response object so no need to check for that)
                if res.status == 200:
                    colorObject = (await res.json())["profileUsers"][0]["settings"][12]

                    # 2. Check that we have the right object
                    if colorObject["id"] == "PreferredColor" and colorObject[
                        "value"
                    ].startswith(
                        "https://dlassets-ssl.xboxlive.com/public/content/ppl/colors/"
                    ):
                        print("Found color object")
                        colorUrl = colorObject["value"]
                        print("Found url: %s" % colorUrl)
                        splitUrl = colorUrl.split("/")

                        splitColorJson = splitUrl[7].split(".")  # "00003", "json"

                        # 2.1. Check all aspects of thee url to make sure it's what we expect
                        if (
                            splitUrl[0] == "https:"
                            and splitUrl[1] == ""
                            and splitUrl[2] == "dlassets-ssl.xboxlive.com"
                            and splitUrl[3] == "public"
                            and splitUrl[4] == "content"
                            and splitUrl[5] == "ppl"
                            and splitUrl[6] == "colors"
                            and splitColorJson[0].isdigit()
                            and splitColorJson[1] == "json"
                            and len(splitColorJson) == 2
                        ):
                            # It's what we expect!
                            colorProfile = int(splitColorJson[0])
                            print("Found color profile '%i'" % colorProfile)

                            # This function serves as a callback after we look up the presence via XUID.
                            async def on_finish(res: ClientResponse):
                                json = await res.json()
                                return await self.createUsercolorsResponse(
                                    json["primaryColor"],
                                    json["secondaryColor"],
                                    json["tertiaryColor"],
                                    [
                                        "X-XBL-WEB-API-Colors-Source",
                                        "%i <%s>" % (colorProfile, colorUrl),
                                    ],
                                )

                            # Request color information, with a callback (same thing as above but connecting externally)
                            return await self.get(
                                "https://dlassets-ssl.xboxlive.com/public/content/ppl/colors/%s.json"
                                % f"{colorProfile:05d}",
                                on_finish,
                            )

            # Make a async request to our own /profile/settings/xuid/ endpoint, awaiting on_finish as a callback
            # on_finish will return our crafted response, so we can return the output once awaited
            return await self.get(
                "http://localhost:%i/profile/settings/xuid/%s"
                % (self.xbl_client._xbl_web_api_current_port, xuid),
                on_finish,
            )

        @self.xbl_decorator.cachedRoute("/get/gamertag/<gamertag>")
        async def getGamertag(gamertag):
            # 1. Convert gamertag to XUID
            # NOTE: We could just call profileSettings via gamertag
            # but if we convert to XUID we can use cached results from /usercolors/get/xuid
            # ----------
            # Making local http requests so we can grab cached data,
            # minimizing the amount of calls made to Xbox Live.
            # See xuid.py#L34
            async def on_xuid_lookup_finish(res: ClientResponse):
                # 1. Check status code
                if res.status == 200:
                    # Assumme we got the data
                    # Get the body
                    body = await res.text()
                    # Parse as JSON
                    data = json.loads(body)
                    # Get the xuid string from the json object
                    xuid = data["xuid"]

                    # 2. Call getXuid (defined above) with our xuid
                    #    We are doing this instead of re-implementing with gamertag input
                    #    So we can make better use of the cache (eg. if user was looked up with gamertag and xuid)
                    async def on_colors_request_finish(svgReq: ClientResponse):
                        if svgReq.status == 200:
                            # Copy useful headers from the response
                            headers = {
                                "x-upstream-queried-at": svgReq.headers.get(
                                    "x-queried-at"
                                ),
                                "x-xbl-web-api-colors-source": svgReq.headers.get(
                                    "x-xbl-web-api-colors-source"
                                ),
                            }
                            # We got the response we were expecting! We can just return it.
                            return Response(
                                await svgReq.text(),
                                headers=headers,
                                mimetype=svgReq.content_type,
                            )
                        else:
                            # MAKE THIS
                            response = jsonify(
                                {
                                    "error": "error getting user colors",
                                    "code": svgReq.status,
                                }
                            )
                            response.status_code = 404
                            return response

                    # Make a async request to our own usercolors/xuid endpoint, using the above callback
                    # Return whatever was returned by the callback
                    return await self.get(
                        "http://localhost:%i/usercolors/get/xuid/%s"
                        % (self.xbl_client._xbl_web_api_current_port, xuid),
                        on_colors_request_finish,
                    )

                # on_xuid_lookup_finish -> if status code is NOT 200
                else:
                    response = jsonify(
                        {"error": "could not resolve gamertag", "code": res.status}
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
