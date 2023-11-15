    def precompute(
            self, mask=None, radius_of_influence=10000, epsilon=0, reduce_data=True, nprocs=1, segments=None,
            cache_dir=False, **kwargs):
        """Create a KDTree structure and store it for later use.

        Note: The `mask` keyword should be provided if geolocation may be valid where data points are invalid.
        This defaults to the `mask` attribute of the `data` numpy masked array passed to the `resample` method.
        """

        del kwargs

        source_geo_def = mask_source_lonlats(self.source_geo_def, mask)

        kd_hash = self.get_hash(source_geo_def=source_geo_def,
                                radius_of_influence=radius_of_influence,
                                epsilon=epsilon)

        filename = self._create_cache_filename(cache_dir, kd_hash)
        self._read_params_from_cache(cache_dir, kd_hash, filename)

        if self.cache is not None:
            LOG.debug("Loaded kd-tree parameters")
            return self.cache
        else:
            LOG.debug("Computing kd-tree parameters")

        valid_input_index, valid_output_index, index_array, distance_array = \
            get_neighbour_info(source_geo_def,
                               self.target_geo_def,
                               radius_of_influence,
                               neighbours=1,
                               epsilon=epsilon,
                               reduce_data=reduce_data,
                               nprocs=nprocs,
                               segments=segments)

        # it's important here not to modify the existing cache dictionary.
        self.cache = {"valid_input_index": valid_input_index,
                      "valid_output_index": valid_output_index,
                      "index_array": index_array,
                      "distance_array": distance_array,
                      "source_geo_def": source_geo_def,
                      }

        self._update_caches(kd_hash, cache_dir, filename)

        return self.cache