from flask import Response

import functools
import logging

# Get a logger instance
logger = logging.getLogger(__name__)

import cache

class CachedRoute:
    # Class init takes blueprint argument
    def __init__(self, app):
        self.app = app

    def __addHeaders__(self, func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            # Call the function
            value = func(*args, **kwargs)
            # Debug log the return type
            logger.debug("__addHeaders__:func return '%s'" % str(value))
            # Return the function output (<Response>) wrapped in add_cache_headers
            return cache.add_cache_headers(value)
        return wrapper_decorator
    
    def __makeJsonResponse__(self, func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            # Call the function
            data = func(*args, **kwargs)
            # Debug log the original return type
            logger.debug("__makeJsonResponse__:func return '%s'" % str(data))
            # Convert the text into a JSON response
            res = Response(response=data, mimetype='application/json')
            logger.debug("__makeJsonResponse__:created '%s'" % str(res))
            # Return the response
            return res
        return wrapper_decorator


    def route(self, path, timeout=300):
        def dec(func):
            logger.debug("Registering route '%s' with cache timeout '%is'" % (path, timeout))
            return self.app.route(path)(cache.cache.cached(timeout)(self.__addHeaders__(func)))
        return dec
    
    def jsonRoute(self, path, timeout=300):
        def dec(func):
            return self.route(path, timeout)(self.__makeJsonResponse__(func))
        return dec
    

