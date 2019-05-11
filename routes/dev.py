from flask import Blueprint, jsonify

import server
import main

app = Blueprint(__name__.split(".")[1], __name__)


@app.route("/reauth")
def reauth():
    main.authenticate()
    return jsonify({"message": "success"})
