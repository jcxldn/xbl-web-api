#from inspect import isawaitable
from asyncio.coroutines import iscoroutinefunction
#from asyncio.futures import isfuture

import base64
import functools
import hashlib
import time

from quart import Response, request

class QuartDecorator(object):
    def __init__(self, app, loop, cache):
        print("quartdecorator init")
        self.app = app
        self.loop = loop
        self.cache = cache
    
    def __debug_return(self, func):
        # Wrap function so function name is set to func's name
        # Required as quart needs different "endpoints" (based on func name) for different routes
        # More info: https://stackoverflow.com/a/42254713
        # Also see: XblDecoratorProvider.py
        @functools.wraps(func)
        def dec(*args, **kwargs):
            value = self.call(func, *args, **kwargs)
            #value = self.call(func)
            #print("RETURN OF FUNC: %s" % value)
            return value
        return dec
    
    def call_async_wait(self, func, *args, **kwargs):
        return self.loop.sync_wait(func(*args, **kwargs))
    
    # is$X functions from asyncio tasks.py
    def call(self, func, *args, **kwargs):
        if iscoroutinefunction(func):
            print("call | coroutine_function")
            return self.call_async_wait(func, *args, **kwargs)
            raise TypeError("Unsupported input func: '%s'" % func)
        
    
    def __cache_response(self, func):
        """
        Internal function to run a route and cache the resulting Response object.
        """
        @functools.wraps(func)
        def dec(*args, **kwargs):
            # Use debug return as calling mechanism (as in router) until we remove it later in the dev stage
            value = self.__debug_return(func)(*args, **kwargs)

            # Next, let's add an X-Queried-At header so we client can easily tell when they recieve a cached result
            value = self.__add_cache_headers(value)

            print("__cache_response")
            print("Is value of type response? %r" % isinstance(value, Response))
            print(value)
            print("has request?")
            print(request.path)
            print("-----")
            print("Hashing path...")
            cache_key = self.__make_cache_key(request)
            print(cache_key)
            print("Sanity check: Checking that 2nd run returns same value...")
            print("Value matches?")
            print(cache_key == self.__make_cache_key(request))

            # Now that we've created the key, we can add it to the cache.
            self.cache.set(cache_key, value, 3600)
            # Lastly, let's return the response so we can complete the request.
            return value
        return dec

    def __add_cache_headers(self, res):
        """
        Helper function to add an X-Queried-At header to a response
        """
        if isinstance(res, Response):
            print("Adding cache headers...")
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
            print("Skipping cache headers (not type Response)")
        return res
    
    def __cachedRoute(self, func):
        """
        Cached Route handler, runs just before app.route.

        This will check the request to see if it's in the cache.
        If it's available, we will return the cached result.
        Otherwise, we'll run the function and __cache_response will cache it.
        """
        @functools.wraps(func)
        def dec(*args, **kwargs):
            print("\n\n\nCACHED ROUTE INIT")
            cache_key = self.__make_cache_key(request)

            # Check if the cache key already exists
            if (self.cache.has(cache_key)):
                # This request is already cached! Let's fetch and return it.
                print("FOUND CACHED RESULT RETURNING")
                return self.cache.get(cache_key)
            else:
                # Result not cached, let's call the function
                print("NO CACHE, CALLING FUNC")
                return self.__cache_response(func)(*args, **kwargs)
        return dec
    
    def __make_cache_key(self, request):
        # 1. Create a hash object
        # TODO: switch to a better hashing algorithm?
        hash = hashlib.sha256()

        # 2. Encode the path in utf-8 (returns in bytes)
        path_encoded = request.path.encode("utf-8")

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
            return self.app.route(path)(self.__cachedRoute(func))
        return dec