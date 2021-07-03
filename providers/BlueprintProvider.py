from abc import ABC, abstractmethod
from quart import Blueprint, jsonify

from providers.XblDecoratorProvider import XblDecorator

class BlueprintProvider(ABC):
    # src: https://stackoverflow.com/a/11408458
    def _type(self):
        return self.__class__.__name__

    def __init__(self, loop, xbl_client):
        self.app = Blueprint(self._type(), self._type())
        print("Init blueprint with name '%s'" % self.app.name)

        self.loop = loop
        self.xbl_client = xbl_client

        self.xbl_decorator = XblDecorator(self.app, self.loop)

        # Shortcut to access openXboxRoute
        self.openXboxRoute = self.xbl_decorator.openXboxRoute

        # Register routes
        self.routes()
    
    @abstractmethod
    def routes(self):
        # decorator handles error reporting, doesn't matter what we put here
        raise NotImplementedError("Implemented in subclass!")