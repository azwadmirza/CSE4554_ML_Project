    def _read_params_from_cache(self, cache_dir, hash_str, filename):
        """Read resampling parameters from cache"""
        self.cache = self.caches.pop(hash_str, None)
        if self.cache is not None and cache_dir:
            self.dump(filename)
        elif os.path.exists(filename):
            self.cache = dict(np.load(filename))
            self.caches[hash_str] = self.cache