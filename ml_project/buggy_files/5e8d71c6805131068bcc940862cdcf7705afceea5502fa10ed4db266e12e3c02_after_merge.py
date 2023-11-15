    def precompute(self, mask=None, radius_of_influence=50000,
                   reduce_data=True, nprocs=1, segments=None,
                   cache_dir=False, **kwargs):
        """Create bilinear coefficients and store them for later use.

        Note: The `mask` keyword should be provided if geolocation may be valid
        where data points are invalid. This defaults to the `mask` attribute of
        the `data` numpy masked array passed to the `resample` method.
        """

        del kwargs

        source_geo_def = mask_source_lonlats(self.source_geo_def, mask)

        bil_hash = self.get_hash(source_geo_def=source_geo_def,
                                 radius_of_influence=radius_of_influence,
                                 mode="bilinear")

        filename = self._create_cache_filename(cache_dir, bil_hash)
        self._read_params_from_cache(cache_dir, bil_hash, filename)

        if self.cache is not None:
            LOG.debug("Loaded bilinear parameters")
            return self.cache
        else:
            LOG.debug("Computing bilinear parameters")

        bilinear_t, bilinear_s, input_idxs, idx_arr = get_bil_info(source_geo_def, self.target_geo_def,
                                                                   radius_of_influence, neighbours=32,
                                                                   nprocs=nprocs, masked=False)
        self.cache = {'bilinear_s': bilinear_s,
                      'bilinear_t': bilinear_t,
                      'input_idxs': input_idxs,
                      'idx_arr': idx_arr}

        self._update_caches(bil_hash, cache_dir, filename)

        return self.cache