from aiohttp import ClientResponse
from quart import Response, render_template

from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider

class Usercolors(BlueprintProvider, LoopbackRequestProvider):
    async def createUsercolorsResponse(self, primary, secondary, tertiary, *headers):
        r = await render_template("usercolors.esvg", primary=primary, secondary=secondary, tertiary=tertiary)
        print(type(r))
        return Response(r, mimetype="image/svg+xml", headers=headers)

    def routes(self):
        @self.xbl_decorator.cachedRoute("/define/<primary>/<secondary>/<tertiary>")
        async def define(primary, secondary, tertiary):
            return (await self.createUsercolorsResponse(primary, secondary, tertiary, ["X-XBL-WEB-API-Colors-Source", "defined"]))

        @self.xbl_decorator.cachedRoute("/get/xuid/<int:xuid>")
        async def getXuid(xuid):
            # 1. Get profile data (/profile/gamertag/)
            #    See: xuid.py#L34

            # This is a callback for after the localhost request has been made.
            async def on_finish(res: ClientResponse):
                # Check status code
                # (If we get here we already have a response object so no need to check for that)
                if (res.status == 200):
                    colorObject = (await res.json())["profileUsers"][0]["settings"][12]

                    # 2. Check that we have the right object
                    if (colorObject["id"] == "PreferredColor" and colorObject["value"].startswith("http://dlassets.xboxlive.com/public/content/ppl/colors/")):
                        print("Found color object")
                        colorUrl = colorObject["value"]
                        print("Found url: %s" % colorUrl)
                        splitUrl = colorUrl.split("/")

                        splitColorJson = splitUrl[7].split(".") # "00003", "json"

                        # 2.1. Check all aspects of thee url to make sure it's what we expect
                        if (
                            splitUrl[0] == "http:" and
                            splitUrl[1] == "" and
                            splitUrl[2] == "dlassets.xboxlive.com" and
                            splitUrl[3] == "public" and
                            splitUrl[4] == "content" and
                            splitUrl[5] == "ppl" and
                            splitUrl[6] == "colors" and
                            splitColorJson[0].isdigit() and
                            splitColorJson[1] == "json" and
                            len(splitColorJson) == 2
                        ):
                            # It's what we expect!
                            colorProfile = int(splitColorJson[0])
                            print("Found color profile '%i'" % colorProfile)

                            # This function serves as a callback after we look up the presence via XUID.
                            async def on_finish(res: ClientResponse):
                                json = await res.json()
                                return await self.createUsercolorsResponse(json["primaryColor"], json["secondaryColor"], json["tertiaryColor"], ["X-XBL-WEB-API-Colors-Source", "%i <%s>" % (colorProfile, colorUrl)])

                            # Request color information, with a callback (same thing as above but connecting externally)
                            return await self.get("https://dlassets-ssl.xboxlive.com/public/content/ppl/colors/%s.json" % f'{colorProfile:05d}', on_finish)
            
            # Make a async request to our own /profile/settings/xuid/ endpoint, awaiting on_finish as a callback
            # on_finish will return our crafted response, so we can return the output once awaited
            return await self.get("http://localhost:%i/profile/settings/xuid/%s" % (self.xbl_client._xbl_web_api_current_port, xuid), on_finish)


#@cr.route("/get/gamertag/<gamertag>", 86400)
#def getGamertag(gamertag):
#    # make the request
#    req = routes.xuid.gamertag_to_xuid_raw(gamertag)
#    # if an error was recieved (it will return an object), return the error
#    if (not routes.xuid.isInt(req)):
#        return req
#    # if there were no errors, return the usual response
#    return getXuid(req)
