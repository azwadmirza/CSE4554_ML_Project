    def resize_all_caches(self):
        """Ensure all cache sizes are up to date

        For each cache, run the mapped callback function with either
        a specific cache factor or the default, global one.
        """
        for cache_name, callback in _CACHES.items():
            new_factor = self.cache_factors.get(cache_name, self.global_factor)
            callback(new_factor)