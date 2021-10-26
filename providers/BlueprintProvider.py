from abc import ABC, abstractmethod
from quart import Blueprint, jsonify

from providers.XblDecoratorProvider import XblDecorator
from providers import LoggingProvider

class BlueprintProvider(ABC):
    # src: https://stackoverflow.com/a/11408458
    def _type(self):
        return self.__class__.__name__

    def __init__(self, loop, xbl_client, cache):
        self.app = Blueprint(self._type(), self._type())
        self.logger = LoggingProvider.getLogger(__name__)

        self.logger.info("Init blueprint with name '%s'" % self.app.name)

        self.loop = loop
        self.xbl_client = xbl_client

        # Set cache variable
        self.cache = cache
        # Pass through cache variable to XblDecorator instance (for openXboxRoute caching in blueprints)
        self.xbl_decorator = XblDecorator(self.app, self.loop, cache)

        # Shortcut to access openXboxRoute
        self.openXboxRoute = self.xbl_decorator.openXboxRoute

        # Register routes
        self.routes()
    
    @abstractmethod
    def routes(self):
        # decorator handles error reporting, doesn't matter what we put here
        raise NotImplementedError("Implemented in subclass!")