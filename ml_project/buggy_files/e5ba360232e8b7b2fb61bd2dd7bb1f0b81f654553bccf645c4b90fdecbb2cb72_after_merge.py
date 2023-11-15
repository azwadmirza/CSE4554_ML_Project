    def _save_cache(self):
        """Save data to the cache file."""
        # Create the cache directory
        safe_makedirs(self.cache_dir)

        # Create/overwrite the cache file
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            logger.error("Cannot write version to cache file {} ({})".format(self.cache_file, e))