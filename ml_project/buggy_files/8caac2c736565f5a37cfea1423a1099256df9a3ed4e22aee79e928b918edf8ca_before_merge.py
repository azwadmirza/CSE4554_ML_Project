    def _update_caches(self, hash_str, cache_dir, filename):
        """Update caches and dump new resampling parameters to disk"""
        self.caches[hash_str] = self.cache
        while len(self.caches) > CACHE_SIZE:
            self.caches.popitem(False)

        if cache_dir:
            # XXX: Look in to doing memmap-able files instead
            # `arr.tofile(filename)`
            self.dump(filename)