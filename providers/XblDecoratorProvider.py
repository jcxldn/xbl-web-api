# Subclass of QuartDecoratorProvider with functions more specific to handling eg. caching & openxbox returning

from providers.QuartDecoratorProvider import QuartDecorator
from providers.modifiers.PagedResponseModifier import PagedResponseModifier

from quart import Response
from humps import camelize
import json
from datetime import datetime, time
import functools


class DateTimeJsonEncoder(json.JSONEncoder):
    # 2017-09-20T15:00:00Z
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat().replace("+00:00", "Z")
        if isinstance(obj, time):
            # Note: v1 openxbox api responses were 7 digits for microseconds, v2 appears to be 6.
            # eg. an ISO of "2016-01-30T17:01:33.0204045Z" is now "2016-01-30T17:01:33.020404Z"
            return obj.isoformat().replace("+00:00", "Z")
        # If not datetime, use super func
        return super(DateTimeJsonEncoder, self).default(obj)


class XblDecorator(QuartDecorator, PagedResponseModifier):
    def __handleOpenXboxRoute(self, func):
        # Wrap function so function name is set to func's name
        # Required as quart needs different "endpoints" (based on func name) for different routes
        # More info: https://stackoverflow.com/a/42254713
        @functools.wraps(func)
        def dec(*args, **kwargs):
            # OpenXBOX calls return a model
            model = self.call(func, *args, **kwargs)

            # If an @openxboxroute returns a response (eg. presence gamertag returns
            # a response with a 404 if it can't resolve the gamertag to an xuid)
            if type(model) is Response:
                # Skip all the openxbox -> formatted response as it would error out
                # and just return the response
                return model

            # Convert the model into a dict, and camelize it (to appear same as pre-v2)
            data = camelize(model.dict())

            # print(data)

            # JSON serialize datetime objects

            data_json = json.dumps(data, cls=DateTimeJsonEncoder, separators=(",", ":"))

            res = Response(response=data_json, mimetype="application/json")

            self.logger.debug("handleOpenXboxRoute: returning: " + str(res))
            return res

        return dec

    def openXboxRoute(self, path, timeout=300):
        def dec(func):
            #    return self.app.route(path)(self.__handleOpenXboxRoute(func))
            return self.cachedRoute(path, timeout)(self.__handleOpenXboxRoute(func))

        return dec
