    def get_dataset(self, key, info):
        """Load a dataset."""
        if self.channel != key.name:
            return
        logger.debug('Reading %s.', key.name)

        radiances = self.nc[self.channel + '_radiance']

        if key.calibration == 'reflectance':
            idx = int(key.name[2:]) - 1
            sflux = self._get_solar_flux(idx)
            radiances = radiances / sflux * np.pi * 100
            radiances.attrs['units'] = '%'

        radiances.attrs['platform_name'] = self.platform_name
        radiances.attrs['sensor'] = self.sensor
        radiances.attrs.update(key.to_dict())
        return radiances