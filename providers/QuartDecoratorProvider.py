from inspect import isfunction
from asyncio.coroutines import iscoroutinefunction

# from asyncio.futures import isfuture

import base64
import functools
import hashlib
import time

from quart import Response, request

from providers import LoggingProvider


class QuartDecorator(object):
    def __init__(self, app, loop, cache):
        self.app = app
        self.loop = loop
        self.cache = cache
        self.logger = LoggingProvider.getLogger(__name__)
        # Log to debug console about decorator init
        self.logger.debug("QuartDecorator init...")

    def __debug_return(self, func):
        # Wrap function so function name is set to func's name
        # Required as quart needs different "endpoints" (based on func name) for different routes
        # More info: https://stackoverflow.com/a/42254713
        # Also see: XblDecoratorProvider.py
        @functools.wraps(func)
        def dec(*args, **kwargs):
            value = self.call(func, *args, **kwargs)
            # value = self.call(func)
            # print("RETURN OF FUNC: %s" % value)
            return value

        return dec

    def call_async_wait(self, func, *args, **kwargs):
        return self.loop.sync_wait(func(*args, **kwargs))

    # is$X functions from asyncio tasks.py
    def call(self, func, *args, **kwargs):
        # Get a child logger with this function name as the suffix
        logger = self.logger.getChild("call")

        if iscoroutinefunction(func):
            logger.debug("Found coroutine function!")
            return self.call_async_wait(func, *args, **kwargs)
        # OpenXbox routes are wrapped in a synchronous handle function
        # Which itself calles this call function
        # So, if we get a normal function, just run it!
        elif isfunction(func):
            logger.debug("Found (normal) function!")
            return func(*args, **kwargs)
        else:
            raise TypeError("Unsupported input func: '%s'" % func)

    def __cache_response(self, func, timeout):
        """
        Internal function to run a route and cache the resulting Response object.
        """

        # Get a child logger with this function name as the suffix
        logger = self.logger.getChild("__cache_response")

        @functools.wraps(func)
        def dec(*args, **kwargs):
            # Use debug return as calling mechanism (as in router) until we remove it later in the dev stage
            value = self.__debug_return(func)(*args, **kwargs)

            # Next, let's add an X-Queried-At header so we client can easily tell when they recieve a cached result
            value = self.__add_cache_headers(value)

            logger.debug("Is value of type response? '%r'", isinstance(value, Response))
            logger.debug("Value Type: '%s'", str(value))
            logger.debug("Has request? '%s'", request.full_path)

            # Now, let's create the cache key by hashing the path.
            cache_key = self.__make_cache_key(request)
            # And log the result!
            logger.info("Created cache key '%s'", cache_key)

            # DEV: Sanity check to make sure 2nd cache key returns the same value
            logger.info(
                "Sanity check passed? %r", cache_key == self.__make_cache_key(request)
            )

            logger.info("Found timeout of %ss", str(timeout))

            # Now that we've created the key, we can add it to the cache.
            self.cache.set(cache_key, value, timeout)

            # Lastly, let's return the response so we can complete the request.
            return value

        return dec

    def __add_cache_headers(self, res):
        """
        Helper function to add an X-Queried-At header to a response
        """

        # Get a child logger with this function name as the suffix
        logger = self.logger.getChild("__add_cache_headers")

        if isinstance(res, Response):

            logger.debug("Adding cache headers...")
            # ----------
            # Create a X-Queried-At header
            # ----------
            # 1. Get the epoch
            epoch = time.time()
            # 2. Convert it to ASCII bytes (?)
            epoch_str_bytes = str(epoch).encode("ascii")
            # 3. Base64 encode the bytes
            epoch_b64 = base64.b64encode(epoch_str_bytes)
            res.headers["X-Queried-At"] = epoch_b64
        else:
            logger.warn("Skipping cache headers (not type Response)")
        return res

    def __cachedRoute(self, func, timeout):
        """
        Cached Route handler, runs just before app.route.

        This will check the request to see if it's in the cache.
        If it's available, we will return the cached result.
        Otherwise, we'll run the function and __cache_response will cache it.
        """

        # Get a child logger with this function name as the suffix
        logger = self.logger.getChild("__cachedRoute")

        @functools.wraps(func)
        def dec(*args, **kwargs):
            logger.debug("dec() called, cached route init")
            cache_key = self.__make_cache_key(request)

            # Check if the cache key already exists
            if self.cache.has(cache_key):
                # This request is already cached! Let's fetch and return it.
                logger.debug("Found cached result! Returning...")
                return self.cache.get(cache_key)
            else:
                # Result not cached, let's call the function
                logger.debug("No cache! Calling function...")
                return self.__cache_response(func, timeout)(*args, **kwargs)

        return dec

    def __make_cache_key(self, request):
        # 1. Create a hash object
        # TODO: switch to a better hashing algorithm?
        hash = hashlib.sha256()

        # 2. Encode the path in utf-8 (returns in bytes)
        path_encoded = request.full_path.encode("utf-8")

        # 3. Base64 encode the path (takes byte input)
        path_b64 = base64.b64encode(path_encoded)

        # 4. Feed the path into the hash object
        hash.update(path_b64)

        # 5. Return the digest (result) of the hash function
        return hash.hexdigest()

    def router(self, path, timeout=300):
        def dec(func):
            return self.app.route(path)(self.__debug_return(func))

        return dec

    def cachedRoute(self, path, timeout=300):
        def dec(func):
            return self.app.route(path)(self.__cachedRoute(func, timeout))

        return dec
