from aiohttp import ClientResponseError, ClientResponse
from quart import jsonify

import json

from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider

# Putting this function outside of the class so that profile.py can access it easily
# TODO: This is not used internally, move to profile.py
def isXUID(xuid):
    return True if len(str(xuid)) == 16 else False


class Xuid(BlueprintProvider, LoopbackRequestProvider):
    def routes(self):
        @self.xbl_decorator.cachedRoute("/<gamertag>")
        async def gamertag_to_xuid(gamertag):
            try:
                profile_response = (
                    await self.xbl_client.profile.get_profile_by_gamertag(gamertag)
                )
                # Return "Gamertag" settings[0] instead of "ModernGamertag" settings[1]
                return jsonify(
                    {
                        "gamertag": profile_response.profile_users[0].settings[0].value,
                        "xuid": profile_response.profile_users[0].id,
                    }
                )

            # Likely a 404
            except ClientResponseError as err:
                response = jsonify(
                    {"error": "could not resolve gamertag", "code": err.code}
                )
                # If we don't get a 404 (eg a 429 too many requests), change the response body
                if err.code != 404:
                    response = jsonify(
                        {"error": "error contacting service", "code": err.code}
                    )
                response.status_code = 404
                return response

        @self.xbl_decorator.cachedRoute("/<gamertag>/raw")
        async def gamertag_to_xuid_raw(gamertag):
            # Here we *could* just call the other function directly
            # While it would be cached, the path would not update
            # So we end up with two cache items for the same path (not good!)
            # This is a problem as one of them has the wrong output (/gamertag call could return /gamertag/raw result!)
            # So instead, we're gonna do what we do in presence.py and make a loopback request
            # To be clear, making a http request to yourself *is not* a good idea
            # ... but at least this way caching works properly :upside_down_face:

            async def on_finish(res: ClientResponse):
                # 1. Check status code
                if res.status == 200:
                    # 200! Assume we got the data
                    text = await res.text()
                    data = json.loads(text)
                    # Return the raw string
                    return data["xuid"]
                else:
                    # Passthough response content (handled in above route)
                    output = jsonify(await res.json())
                    # Set a 404 (actual response code is res.content.code)
                    output.status_code = 404
                    # Return the response object
                    return output

            return await self.get(
                "http://localhost:%i/xuid/%s"
                % (self.xbl_client._xbl_web_api_current_port, gamertag),
                on_finish,
            )
