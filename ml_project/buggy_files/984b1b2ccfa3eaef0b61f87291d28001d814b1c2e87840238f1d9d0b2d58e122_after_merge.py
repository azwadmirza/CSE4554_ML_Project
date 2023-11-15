    def get_dataset(self, key, info=None):
        """Load a dataset
        """
        if key in self.cache:
            return self.cache[key]

        logger.debug('Reading {}'.format(key.name))
        # Get the dataset
        # Get metadata for given dataset
        variable = self.nc['/data/{}/measured/effective_radiance'
                           .format(key.name)]
        # Convert to xarray
        radiances = xr.DataArray(np.asarray(variable, np.float32), dims=['y', 'x'])
        radiances.attrs['scale_factor'] = variable.attrs['scale_factor']
        radiances.attrs['offset'] = variable.attrs.get('add_offset', 0)
        radiances.attrs['FillValue'] = variable.attrs['_FillValue']
        # Set invalid values to NaN
        radiances.values[radiances == radiances.attrs['FillValue']] = np.nan
        # Apply scale factor and offset
        radiances = radiances * (radiances.attrs['scale_factor'] * 1.0) + radiances.attrs['offset']

        #TODO Calibration is disabled, waiting for calibration parameters from EUMETSAT
        res = self.calibrate(radiances, key)

        self.cache[key] = res
        self.nlines, self.ncols = res.shape

        return res