    def get_dataset(self, key, info):
        """Load a dataset."""
        if key.name not in self.datasets:
            return

        if self.nc is None:
            self.nc = h5netcdf.File(self.filename, 'r')

        logger.debug('Reading %s.', key.name)

        l_step = self.nc.attrs['al_subsampling_factor']
        c_step = self.nc.attrs['ac_subsampling_factor']

        if (c_step != 1 or l_step != 1) and key.name not in self.cache:

            if key.name.startswith('satellite'):
                zen, zattrs = self._get_scaled_variable(
                    self.datasets['satellite_zenith_angle'])
                azi, aattrs = self._get_scaled_variable(
                    self.datasets['satellite_azimuth_angle'])
            elif key.name.startswith('solar'):
                zen, zattrs = self._get_scaled_variable(
                    self.datasets['solar_zenith_angle'])
                azi, aattrs = self._get_scaled_variable(
                    self.datasets['solar_azimuth_angle'])
            else:
                raise NotImplementedError("Don't know how to read " + key.name)

            x, y, z = angle2xyz(azi, zen)
            shape = x.shape

            from geotiepoints.interpolator import Interpolator
            tie_lines = np.arange(
                0, (shape[0] - 1) * l_step + 1, l_step)
            tie_cols = np.arange(0, (shape[1] - 1) * c_step + 1, c_step)
            lines = np.arange((shape[0] - 1) * l_step + 1)
            cols = np.arange((shape[1] - 1) * c_step + 1)
            along_track_order = 1
            cross_track_order = 3
            satint = Interpolator([x, y, z],
                                  (tie_lines, tie_cols),
                                  (lines, cols),
                                  along_track_order,
                                  cross_track_order)
            (x, y, z, ) = satint.interpolate()

            azi, zen = xyz2angle(x, y, z)

            if 'zenith' in key.name:
                values, attrs = zen, zattrs
            elif 'azimuth' in key.name:
                values, attrs = azi, aattrs
            else:
                raise NotImplementedError("Don't know how to read " + key.name)

            if key.name.startswith('satellite'):
                self.cache['satellite_zenith_angle'] = zen, zattrs
                self.cache['satellite_azimuth_angle'] = azi, aattrs
            elif key.name.startswith('solar'):
                self.cache['solar_zenith_angle'] = zen, zattrs
                self.cache['solar_azimuth_angle'] = azi, aattrs

        elif key.name in self.cache:
            values, attrs = self.cache[key.name]
        else:
            values, attrs = self._get_scaled_variable(self.datasets[key.name])

        units = attrs['units']

        proj = Dataset(values,
                       copy=False,
                       units=units,
                       platform_name=self.platform_name,
                       sensor=self.sensor)
        proj.info.update(key.to_dict())
        return proj