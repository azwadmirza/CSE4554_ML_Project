    def resample(self, data, cache_dir=False, mask_area=True, **kwargs):
        """Resample the *data*, saving the projection info on disk if *precompute* evaluates to True.

        :param mask_area: Provide data mask to `precompute` method to mask invalid data values in geolocation.
        """
        if mask_area and hasattr(data, "mask"):
            kwargs.setdefault("mask", data.mask)
        cache_id = self.precompute(cache_dir=cache_dir, **kwargs)
        return self.compute(data, cache_id=cache_id, **kwargs)