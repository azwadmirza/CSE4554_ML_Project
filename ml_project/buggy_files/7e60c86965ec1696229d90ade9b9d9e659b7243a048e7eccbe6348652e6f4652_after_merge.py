    def get_dataset(self, key, info, out=None, xslice=slice(None), yslice=slice(None)):
        """Load a dataset."""
        # Read bands
        data = self.read_band(key, info)
        # Convert to xarray
        xdata = xr.DataArray(data, dims=['y', 'x'])
        # Mask invalid values
        return xdata