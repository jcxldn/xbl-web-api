from flask import Blueprint, Response, render_template, jsonify

import json
import requests

import server

import routes.profile
import routes.xuid

from cached_route import CachedRoute

app = Blueprint(__name__.split(".")[1], __name__)
cr = CachedRoute(app)


def usercolors(primary, secondary, tertiary, *headers):
    r = render_template("usercolors.esvg", primary=primary,
                        secondary=secondary, tertiary=tertiary)
    return Response(r, mimetype="image/svg+xml", headers=headers)


@cr.route("/define/<primary>/<secondary>/<tertiary>")
def define(primary, secondary, tertiary):
    return usercolors(primary, secondary, tertiary)


@cr.route("/get/xuid/<int:xuid>")
def getXuid(xuid):
    profileData = json.loads((routes.profile.xuid(xuid)).data)
    colorObj = profileData["profileUsers"][0]["settings"][9]

    # Make sure that we have the right item to prevent malicious URLs being used.
    if (colorObj["id"] == "PreferredColor"):

        # Rewrite the URL to use SSL.
        colorURL = colorObj["value"].replace(
            "http://dlassets.xboxlive.com", "https://dlassets-ssl.xboxlive.com")

        # Make the request
        colorsRequest = requests.get(colorURL)

        if colorsRequest.status_code == 200:
            # Request returned a 200.

            # Get the JSON response.
            colorsData = colorsRequest.json()

            # Return the SVG.
            return usercolors(colorsData["primaryColor"], colorsData["secondaryColor"], colorsData["tertiaryColor"], ["X-XBL-WEB-API-Colors-URL", colorURL])

        else:
            # Request returned a non-200 HTTP code
            return jsonify({"error": 500, "message": "colors request failed"}), 500
    else:
        return jsonify({"error": 500, "message": "preferredColor not found"}), 500


@cr.route("/get/gamertag/<gamertag>")
def getGamertag(gamertag):
    # make the request
    req = routes.xuid.gamertag_to_xuid_raw(gamertag)
    # if an error was recieved (it will return an object), return the error
    if (not routes.xuid.isInt(req)):
        return req
    # if there were no errors, return the usual response
    return getXuid(req)
