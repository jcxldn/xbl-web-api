from abc import ABC, abstractmethod

from providers.XblDecoratorProvider import XblDecorator

from providers.caching.CacheConstants import CacheConstants

class CacheProvider(ABC):
    # src: https://stackoverflow.com/a/11408458
    def _type(self):
        return self.__class__.__name__

    @abstractmethod
    def get(self, key):
        raise NotImplementedError("Implemented in subclass!")
    
    @abstractmethod
    def set(self, key, value, expire_seconds):
        raise NotImplementedError("Implemented in subclass!")
    
    @abstractmethod
    def has(self, key):
        raise NotImplementedError("Implemented in subclass")

    @abstractmethod
    def shutdown(self):
        raise NotImplementedError("Implemented in subclass!")

    constants = CacheConstants