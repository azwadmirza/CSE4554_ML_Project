    def precompute(self, **kwargs):
        """Create X and Y indices and store them for later use."""
        LOG.debug("Initializing bucket resampler.")
        source_lons, source_lats = self.source_geo_def.get_lonlats(
            chunks=CHUNK_SIZE)
        self.resampler = bucket.BucketResampler(self.target_geo_def,
                                                source_lons,
                                                source_lats)