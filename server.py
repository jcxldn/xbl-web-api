import os

from flask import Flask, jsonify

app = Flask(__name__)


def run_dev():
    port = os.getenv("PORT") or 3000
    app.run(host='0.0.0.0', port=port)


# define routes
@app.route("/")
def hello():
    return jsonify({"hello": "hello, world!"})
