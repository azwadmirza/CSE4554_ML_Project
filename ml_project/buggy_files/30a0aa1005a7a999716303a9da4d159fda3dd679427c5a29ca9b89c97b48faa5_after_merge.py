    def get_dataset(self, key, info,
                    xslice=slice(None), yslice=slice(None)):
        """Load a dataset."""
        logger.debug('Reading in get_dataset %s.', key.name)

        radiances = self.nc["Rad"][xslice, yslice].expand_dims('time')

        res = self.calibrate(radiances)

        # convert to satpy standard units
        if res.attrs['units'] == '1':
            res = res * 100
            res.attrs['units'] = '%'

        res.attrs.update({'platform_name': self.platform_name,
                          'sensor': self.sensor,
                          'satellite_latitude': float(self.nc['nominal_satellite_subpoint_lat']),
                          'satellite_longitude': float(self.nc['nominal_satellite_subpoint_lon']),
                          'satellite_altitude': float(self.nc['nominal_satellite_height'])})
        res.attrs.update(key.to_dict())

        return res