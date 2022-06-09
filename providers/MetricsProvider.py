from abc import ABC

from aioprometheus import Counter, Gauge
from quart import Quart

from providers.metrics import AppProvider


class MetricsProvider(ABC):
    # src: https://stackoverflow.com/a/11408458
    def _type(self):
        return self.__class__.__name__

    def __init__(self, app: Quart):
        self.metrics_app = AppProvider.AppProvider()

        # Define custom counters
        self.cached_requests_counter = Counter(
            "responses_total_cached_counter", "Total number of cached responses sent"
        )
        self.uncached_requests_counter = Counter(
            "responses_total_uncached_counter",
            "Total number of uncached responses sent",
        )

        self.requests_counter = Counter(
            "requests_total_counter", "Total requests recieved"
        )

        self.cache_size_gauge = Gauge(
            "cache_size", "Unique responses currently stored in the cache"
        )

        app.metrics = self

        # Setup middleware
        app.asgi_app = MetricsMiddleware(app.asgi_app, self)


# Define a middleware to adjust metrics for every request
class MetricsMiddleware:
    def __init__(self, app, metrics: MetricsProvider):
        self.app = app
        self.metrics = metrics

    async def __call__(self, scope, receive, send):
        if "headers" in scope:
            # Find the user-agent header
            # Iterate through each header item
            for i in range(len(scope["headers"])):
                # Check if the decoded string matches
                if scope["headers"][i][0].decode() == "user-agent":
                    # Found it!
                    user_agent = scope["headers"][i][1].decode()
                    self.metrics.requests_counter.inc({"user_agent": user_agent})

        # Continue
        return await self.app(scope, receive, send)
