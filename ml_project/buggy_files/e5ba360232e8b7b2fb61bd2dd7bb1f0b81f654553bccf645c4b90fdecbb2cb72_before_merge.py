    def _save_cache(self):
        """Save data to the cache file."""
        # Create the cache directory
        safe_makedirs(self.cache_dir)

        # Create/overwrite the cache file
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.data, f)