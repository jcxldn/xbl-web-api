from flask import Blueprint, jsonify

import server
import main

app = Blueprint(__name__.split(".")[1], __name__)


@app.route("/reauth")
async def reauth():
    await server.xbl_client._auth_mgr.refresh_tokens()
    return jsonify({"message": "success"})


@app.route("/isauth")
def isauth():
    oauth = server.xbl_client._auth_mgr.oauth.is_valid()
    user = server.xbl_client._auth_mgr.user_token.is_valid()
    xsts = server.xbl_client._auth_mgr.xsts_token.is_valid()
    return jsonify({
        "authenticated": oauth and user and xsts,
        })
