#from inspect import isawaitable
from asyncio.coroutines import iscoroutinefunction
#from asyncio.futures import isfuture

class QuartDecorator(object):
    def __init__(self, app, loop):
        print("quartdecorator init")
        self.app = app
        self.loop = loop
    
    def __debug_return(self, func):
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

    
    def router(self, path, timeout=300):
        def dec(func):
            return self.app.route(path)(self.__debug_return(func))
        return dec