    def precompute(self, mask=None, radius_of_influence=None, epsilon=0,
                   cache_dir=None, **kwargs):
        """Create a KDTree structure and store it for later use.

        Note: The `mask` keyword should be provided if geolocation may be valid
        where data points are invalid.

        """
        del kwargs
        source_geo_def = self.source_geo_def

        if mask is not None and cache_dir is not None:
            LOG.warning("Mask and cache_dir both provided to nearest "
                        "resampler. Cached parameters are affected by "
                        "masked pixels. Will not cache results.")
            cache_dir = None
        # TODO: move this to pyresample
        if radius_of_influence is None:
            try:
                radius_of_influence = source_geo_def.lons.resolution * 3
            except AttributeError:
                try:
                    radius_of_influence = max(abs(source_geo_def.pixel_size_x),
                                              abs(source_geo_def.pixel_size_y)) * 3
                except AttributeError:
                    radius_of_influence = 1000

            except TypeError:
                radius_of_influence = 10000

        kwargs = dict(source_geo_def=source_geo_def,
                      target_geo_def=self.target_geo_def,
                      radius_of_influence=radius_of_influence,
                      neighbours=1,
                      epsilon=epsilon)

        if self.resampler is None:
            # FIXME: We need to move all of this caching logic to pyresample
            self.resampler = XArrayResamplerNN(**kwargs)

        try:
            self.load_neighbour_info(cache_dir, mask=mask, **kwargs)
            LOG.debug("Read pre-computed kd-tree parameters")
        except IOError:
            LOG.debug("Computing kd-tree parameters")
            self.resampler.get_neighbour_info(mask=mask)
            self.save_neighbour_info(cache_dir, mask=mask, **kwargs)