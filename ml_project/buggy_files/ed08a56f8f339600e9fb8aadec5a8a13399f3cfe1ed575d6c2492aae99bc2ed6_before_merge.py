    def _read_params_from_cache(self, cache_dir, hash_str, filename):
        """Read resampling parameters from cache"""
        try:
            self.cache = self.caches[hash_str]
            # trick to keep most used caches away from deletion
            del self.caches[hash_str]
            self.caches[hash_str] = self.cache

            if cache_dir:
                self.dump(filename)
            return
        except KeyError:
            if os.path.exists(filename):
                self.cache = dict(np.load(filename))
                self.caches[hash_str] = self.cache
                while len(self.caches) > CACHE_SIZE:
                    self.caches.popitem(False)
                if cache_dir:
                    self.dump(filename)
            else:
                self.cache = None