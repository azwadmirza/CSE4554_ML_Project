    def _load_cache(self):
        """Load cache file and return cached data"""
        # If the cached file exist, read-it
        max_refresh_date = timedelta(days=7)
        cached_data = {}
        try:
            with open(self.cache_file, 'rb') as f:
                cached_data = pickle.load(f)
        except Exception as e:
            logger.debug("Cannot read version from cache file: {}".format(e))
        else:
            logger.debug("Read version from cache file")
            if (cached_data['installed_version'] != self.installed_version() or
                    datetime.now() - cached_data['refresh_date'] > max_refresh_date):
                # Reset the cache if:
                # - the installed version is different
                # - the refresh_date is > max_refresh_date
                cached_data = {}
        return cached_data