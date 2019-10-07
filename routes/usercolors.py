from flask import Blueprint, Response, render_template

import server

app = Blueprint(__name__.split(".")[1], __name__)


def usercolors(primary, secondary, tertiary):
    r = render_template("usercolors.esvg", primary=primary,
                        secondary=secondary, tertiary=tertiary)
    return Response(r, mimetype="image/svg+xml")


@app.route("/define/<primary>/<secondary>/<tertiary>")
def define(primary, secondary, tertiary):
    return usercolors(primary, secondary, tertiary)
