import os

from flask import Flask, jsonify

import routes.profile
import routes.xuid

app = Flask(__name__, static_folder=None)


def get_client(main_xbl_client):
    global xbl_client
    xbl_client = main_xbl_client
    routes.profile.get_client(xbl_client)
    routes.xuid.get_client(xbl_client)


def run_dev():
    port = os.getenv("PORT") or 3000
    app.run(host='0.0.0.0', port=port)


def res_as_json(data):
    return app.response_class(response=data, mimetype='application/json')


# add routes / blueprints from other files
app.register_blueprint(routes.profile.app, url_prefix="/profile")
app.register_blueprint(routes.xuid.app, url_prefix="/xuid")

# define routes
@app.route("/")
def hello():
    return jsonify({"hello": "hello, world!"})


@app.route("/routes")
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)
    return jsonify(routes)
