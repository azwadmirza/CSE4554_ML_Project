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
        ds = (np.ma.masked_equal(variable[:],
                                 variable.attrs['_FillValue']) *
              (variable.attrs['scale_factor'] * 1.0) +
              variable.attrs.get('add_offset', 0))

        self.calibrate(ds, key)

        out = Dataset(ds, dtype=np.float32)

        self.cache[key] = out
        self.nlines, self.ncols = ds.shape

        return out