# PagedResponseModifier - a decorator placed under the route decorator to allow for easy continuationToken support.

from quart import request
import functools

def tryParseInt(val, fallback):
        try:
            if val.isdigit():
                return int(val)
            else:
                return fallback
        except AttributeError:
            # val is likely NoneType
            return fallback

class PagedResponseModifier():
    def __handlePagedResponseRoute(self, func):
        @functools.wraps(func)
        def handle(*args, **kwargs):
            # we have imported request from quart
            # At this point it will contain the usual request object as in a normal route
            # So we can interact just as if we are in the route function itself
            continuationToken = tryParseInt(request.args.get("continuationToken"), 0)
            self.logger.debug("pagedResponseModifier: found continuationToken: '%i'" % continuationToken)

            # Add the continuationToken to args
            kwargs["continuationToken"] = continuationToken

            # Return the decorator by calling the passed func
            return self.call(func, *args, **kwargs)
        return handle

    
    def pagedResponseModifier(self):
        def dec(func):
            return self.__handlePagedResponseRoute(func)
        return dec