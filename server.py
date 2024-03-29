# Quart's flask-patch (intended for extensions) adds a loop.sync_wait function used in QuartDecoratorProvider.
import quart.flask_patch
from quart import Quart, jsonify, send_from_directory, request

# Hypercorn (Quart ASGI webserver)
from hypercorn.config import Config
from hypercorn.asyncio import serve

from apscheduler.schedulers.asyncio import AsyncIOScheduler


from routes import Routes
from providers import LoggingProvider
from providers.MetricsProvider import MetricsProvider
from providers.XblDecoratorProvider import XblDecorator
from providers.caching.DiskCacheProvider import DiskCacheProvider

# from flask_cors import CORS

import asyncio
import subprocess
import os
import logging

import main

logger = LoggingProvider.getLogger("server")

loop = asyncio.get_event_loop()
logger.info("Using loop: %s" % str(loop))
app = Quart(__name__, static_folder=None)
xbl_client, session = loop.run_until_complete(main.authenticate(loop))

# Get a MetricsProvider
metrics = MetricsProvider(app)

# Get a cacheprovider
cache = DiskCacheProvider("/tmp/xbl-web-api")

# Setup & start the scheduler
scheduler = AsyncIOScheduler(event_loop=loop)
scheduler.start()

# Define scheduled tasks
sched_logger = logging.getLogger("sched.timed_reauth")


@scheduler.scheduled_job("interval", minutes=1)
async def job_timed_reauth():
    is_same_loop = asyncio.get_running_loop() is loop
    if is_same_loop:
        sched_logger.debug("In the same event loop! Refreshing tokens if needed...")

        issueTimeBeforeRefresh = xbl_client._auth_mgr.user_token.issue_instant
        # This async function will refresh the tokens only *if* they are unavailable or expired
        await xbl_client._auth_mgr.refresh_tokens()

        if xbl_client._auth_mgr.user_token.issue_instant != issueTimeBeforeRefresh:
            sched_logger.debug("Tokens have been refreshed!")
            # Token has changed, save to disk
            with open(os.getenv("XBL_TOKENS_PATH"), mode="w") as f:
                f.write(xbl_client._auth_mgr.oauth.json())
                sched_logger.info("Saved refreshed tokens to disk!")
        else:
            sched_logger.debug("Tokens have NOT been refreshed")
    else:
        sched_logger.error("Not in the same event loop!")
        raise RuntimeError("Timed Reauth not in same loop!")


@scheduler.scheduled_job("interval", minutes=5)
async def job_cache_cleanup():
    # This job will remove expired items from the cache
    number_removed = cache.remove_expired()

    # Get a logger and print details on how much we cleared
    logger = logging.getLogger("sched.cache_cleanup")
    logger.info("Removed %i expired items from cache." % number_removed)
    logger.info("New cache size is %i items." % cache.len())

    # If we removed anything, update the cache size metric
    if number_removed != 0:
        metrics.cache_size_gauge.set({}, cache.len())


# Get the short SHA and return as string
def get_sha():
    if "GIT_COMMIT" in os.environ:
        return os.getenv("GIT_COMMIT")[0:7]
    else:
        return str(
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
        ).split("'")[1::2][0]


def get_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append("%s" % rule)
    return routes


# Import routes from routes/ directory
Routes(app, loop, xbl_client, cache, metrics)

# Define routes for the homepage
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/readme")
async def readme():
    res = await send_from_directory("./", "README.md")
    # Windows sets the wrong mimetype
    res.mimetype = "text/markdown"
    return res


@app.route("/info")
def info():
    return jsonify({"sha": get_sha(), "routes": get_routes()})


# Define routes that don't fit into any other categories
# Create a XblDecorator instance
r = XblDecorator(app, loop, cache, metrics)


@r.openXboxRoute("/titleinfo/<int:titleid>", r.cache.constants.SECONDS_ONE_DAY)
async def titleinfo(titleid):
    return await xbl_client.titlehub.get_title_info(titleid)


# legacysearch (EDS) has been removed from xbox-webapi v2
# It may be possible to re-implement at a later date
@r.cachedRoute("/legacysearch/<query>", r.cache.constants.SECONDS_THIRTY_DAYS)
async def search360(query):
    res = jsonify({"error": "legacysearch not currently available", "code": 410})
    res.status_code = 410  # 410 (Gone)
    return res


@r.cachedRoute("/gamertag/check/<gamertag>", r.cache.constants.SECONDS_ONE_DAY)
async def gamertagcheck(gamertag):
    # Use .value to get the int instead of the enum
    code = (await xbl_client.account.claim_gamertag(1, gamertag)).value
    return jsonify(
        {"available": "true" if code == 200 else "false" if code == 409 else "unknown"}
    )


# Create hypercorn config object
port = int(os.getenv("PORT", 3000))
config = Config()
config.bind = ["0.0.0.0:%i" % port]

# Save the port so we can access it later
# Making loopback requests is a *bad* idea but we do get cached results this way!
xbl_client._xbl_web_api_current_port = port

# Run hypercorn in the same loop as xbl_client
loop.run_until_complete(serve(app, config))

# When we get here, hypercorn has finished so we can just close the ClientSession
logger.info("Serve future done! Closing session...")
loop.run_until_complete(session.close())
# Next up, let's gracefully stop the cache provider
logger.info("Shutting down cache provider... (had %i items)" % cache.len())
cache.shutdown()

logger.info("Waiting for metrics thread to shut down...")
# Let's set the shutdown event for the metrics web server thread...

# Setting the event directly doesn't work on Linux (not thread-safe?)
# metrics.metrics_app.shutdown_event.set()

# Instead we will set the event using the loop for the metrics app.
# see: https://stackoverflow.com/a/48839244
metrics.metrics_app.loop.call_soon_threadsafe(metrics.metrics_app.shutdown_event.set)

while metrics.metrics_app.thread.is_alive():
    continue  # Wait until shutdown

logger.info("Shut down metrics thread!")

# Cleanup done!
logger.info("Cleanup done!")
