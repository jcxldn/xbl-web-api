from flask import Blueprint, jsonify

import server
import main

app = Blueprint(__name__.split(".")[1], __name__)


@app.route("/reauth")
def reauth():
    main.authenticate()
    return jsonify({"message": "success"})


@app.route("/isauth")
def isauth():
    return jsonify({
        "authenticated": main.auth_mgr.authenticated,
        "user": main.auth_mgr.userinfo.gamertag,
        "access": {
            "issued": main.auth_mgr.access_token.date_issued,
            "expires": main.auth_mgr.access_token.date_valid,
            "valid": main.auth_mgr.access_token.is_valid
        },
        "user": {
            "issued": main.auth_mgr.user_token.date_issued,
            "expires": main.auth_mgr.user_token.date_valid,
            "valid": main.auth_mgr.user_token.is_valid
        }})
