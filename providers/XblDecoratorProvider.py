# Subclass of QuartDecoratorProvider with functions more specific to handling eg. caching & openxbox returning

from providers.QuartDecoratorProvider import QuartDecorator

from quart import Response
from humps import camelize
import json
from datetime import datetime

class DateTimeJsonEncoder(json.JSONEncoder):
    # 2017-09-20T15:00:00Z
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat().replace('+00:00', 'Z')
        # If not datetime, use super func
        return super(DateTimeJsonEncoder, self).default(obj)

class XblDecorator(QuartDecorator):

    def __handleOpenXboxRoute(self, func):
        def dec(*args, **kwargs):
            # OpenXBOX calls return a model
            model = self.call(func, *args, **kwargs)

            # Convert the model into a dict, and camelize it (to appear same as pre-v2)
            data = camelize(model.dict())

            print(data)

            # JSON serialize datetime objects

            data_json = json.dumps(data, cls=DateTimeJsonEncoder, separators=(',', ':'))
            
            res = Response(response=data_json, mimetype="application/json")
            return res
        return dec

    def openXboxRoute(self, path, timeout=300):
        def dec(func):
            return self.app.route(path)(self.__handleOpenXboxRoute(func))
        return dec