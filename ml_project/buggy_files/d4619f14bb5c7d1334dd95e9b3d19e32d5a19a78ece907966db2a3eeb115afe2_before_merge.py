    def get_dataset(self, key, info):
        """Load a dataset
        """
        if self.channel != key.name:
            return
        logger.debug('Reading %s.', key.name)
        variable = self.nc[self.channel + '_radiance']

        radiances = (np.ma.masked_equal(variable[:],
                                        variable.attrs['_FillValue'], copy=False) *
                     variable.attrs['scale_factor'] +
                     variable.attrs['add_offset'])
        units = variable.attrs['units']
        if key.calibration == 'reflectance':
            solar_flux = self.cal['solar_flux'][:]
            d_index = np.ma.masked_equal(self.cal['detector_index'][:],
                                         self.cal['detector_index'].attrs[
                                             '_FillValue'],
                                         copy=False)
            idx = int(key.name[2:]) - 1
            radiances /= solar_flux[idx, d_index]
            radiances *= np.pi * 100
            units = '%'

        proj = Dataset(radiances,
                       copy=False,
                       units=units,
                       platform_name=self.platform_name,
                       sensor=self.sensor)
        proj.info.update(key.to_dict())
        return proj