from aioprometheus import REGISTRY, render
from quart import Quart, request

# Hypercorn (Quart ASGI webserver)
from hypercorn.config import Config
from hypercorn.asyncio import serve

import asyncio
import threading


class AppProvider(object):
    def __init__(self):
        thread = threading.Thread(name="MetricsWS", target=self.thread_main)
        thread.start()
        self.thread = thread

    # This function runs in the new thread
    def thread_main(self):
        # Create a new event loop, and set it as the current loop for this thread.
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Get the new loop
        self.loop = asyncio.get_event_loop()

        # Create a secondary quart instance
        app = Quart(__name__, static_folder=None)

        # Create a shutdown event
        self.shutdown_event = asyncio.Event()

        # Define the metrics route
        @app.route("/metrics")
        async def handle_metrics():
            content, http_headers = render(REGISTRY, request.headers.getlist("accept"))
            return content, http_headers

        # Bind on another port
        config = Config()
        config.bind = ["0.0.0.0:%i" % 3001]
        # Start the server
        self.loop.run_until_complete(
            serve(app, config, shutdown_trigger=self.shutdown_event.wait)
        )
