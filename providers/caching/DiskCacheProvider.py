import diskcache

from providers.caching.CacheProvider import CacheProvider

class DiskCacheProvider(CacheProvider):
    def __init__(self, path):
        self.cache = diskcache.Cache(path)
        self.cache.clear()  # Clear all items
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value, expire):
        return self.cache.set(key, value, expire)
    
    def has(self, key):
        return self.cache.__contains__(key)

    def len(self):
        return self.cache.__len__()

    def remove_expired(self):
        return self.cache.expire()
    
    def shutdown(self):
        self.cache.close()
    
    def cached(self, timeout):
        def dec(func):
            return diskcache.memoize(self.cache, timeout)(func)
        return dec