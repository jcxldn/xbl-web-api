
from dogpile.cache import make_region

from dogpile.cache.api import NoValue

region = make_region().configure(
    'dogpile.cache.memory'
)


class CacheProvider():
    def __init__(self):
        self.region = make_region().configure(
            'dogpile.cache.memory'
        )
    
    def has(self, path):
        # If not novalue, return true
        return not isinstance(self.region.get(path), NoValue)
    
    def set(self, path, value):
        self.region.set(path, value)
    
    def get(self, path):
        return self.region.get(path)
        

cp = CacheProvider()