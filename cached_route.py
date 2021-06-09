import functools

import cache

class CachedRoute:
    def __init__(self, app):
        print(app)
        self.app = app

    def __addHeaders__(self, func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            print("----- addHeaders -----")
            # Do something before
            print("before")
            value = func(*args, **kwargs)
            print("after")
            print(value)
            # Do something after
            print("----- addHeaders -----")
            return cache.add_cache_headers(value)
        return wrapper_decorator

    def route(self, path, timeout=300):
        def dec(func):
            print("[CachedRoute] Registering path '%s' with timeout '%is'" % (path, timeout))
            #return cache.cached(timeout)(addHeaders(func))
            return self.app.route(path)(cache.cache.cached(timeout)(self.__addHeaders__(func)))
        return dec
    

