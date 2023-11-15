    def _calibrate(self, data):
        """Calibrate *data*."""
        idx = self.mda['calibration_parameters']['indices']
        val = self.mda['calibration_parameters']['values']
        ddata = data.data.map_blocks(lambda block: np.interp(block, idx, val), dtype=val.dtype)
        res = xr.DataArray(ddata,
                           dims=data.dims, attrs=data.attrs,
                           coords=data.coords)
        res = res.clip(min=0)
        units = {'percent': '%'}
        unit = self.mda['calibration_parameters'][b'_UNIT']
        res.attrs['units'] = units.get(unit, unit)
        return res