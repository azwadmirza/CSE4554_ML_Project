    def resample(self, data, cache_dir=False, mask_area=True, **kwargs):
        """Resample the *data*, saving the projection info on disk if *precompute* evaluates to True.

        :param mask_area: Provide data mask to `precompute` method to mask invalid data values in geolocation.
        """
        if mask_area:
            mask = kwargs.get('mask', np.zeros_like(data, dtype=np.bool))
            if data.attrs.get('_FillValue'):
                mask = xu.logical_and(data, data == data.attrs['_FillValue'])
            if hasattr(data, 'mask'):
                mask = xu.logical_and(data, data.mask)
            elif hasattr(data, 'isnull'):
                mask = xu.logical_and(data, data.isnull())
            summing_dims = [dim for dim in data.dims if dim not in ['x', 'y']]
            mask = mask.sum(dim=summing_dims).astype(bool)
            kwargs['mask'] = mask
        cache_id = self.precompute(cache_dir=cache_dir, **kwargs)
        data.attrs['_last_resampler'] = self
        return self.compute(data, cache_id=cache_id, **kwargs)