    def precompute(self, mask=None, radius_of_influence=50000, epsilon=0,
                   reduce_data=True, cache_dir=False, **kwargs):
        """Create bilinear coefficients and store them for later use."""
        del kwargs
        del mask

        if self.resampler is None:
            kwargs = dict(source_geo_def=self.source_geo_def,
                          target_geo_def=self.target_geo_def,
                          radius_of_influence=radius_of_influence,
                          neighbours=32,
                          epsilon=epsilon,
                          reduce_data=reduce_data)

            self.resampler = XArrayResamplerBilinear(**kwargs)
            try:
                self.load_bil_info(cache_dir, **kwargs)
                LOG.debug("Loaded bilinear parameters")
            except IOError:
                LOG.debug("Computing bilinear parameters")
                self.resampler.get_bil_info()
                LOG.debug("Saving bilinear parameters.")
                self.save_bil_info(cache_dir, **kwargs)