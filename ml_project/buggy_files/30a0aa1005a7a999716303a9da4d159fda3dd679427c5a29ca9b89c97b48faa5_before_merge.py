    def get_dataset(self, key, info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        """Load a dataset."""
        logger.debug('Reading in get_dataset %s.', key.name)

        variable = self.nc["Rad"]

        radiances = (np.ma.masked_equal(variable[yslice, xslice],
                                        variable.attrs['_FillValue'], copy=False) *
                     variable.attrs['scale_factor'] +
                     variable.attrs['add_offset'])
        # units = variable.attrs['units']
        units = self.calibrate(radiances)

        # convert to satpy standard units
        if units == '1':
            radiances[:] *= 100.
            units = '%'

        out.data[:] = radiances
        out.mask[:] = np.ma.getmask(radiances)
        out.info.update({'units': units,
                         'platform_name': self.platform_name,
                         'sensor': self.sensor,
                         'satellite_latitude': self.nc['nominal_satellite_subpoint_lat'][()],
                         'satellite_longitude': self.nc['nominal_satellite_subpoint_lon'][()],
                         'satellite_altitude': self.nc['nominal_satellite_height'][()]})
        out.info.update(key.to_dict())

        return out