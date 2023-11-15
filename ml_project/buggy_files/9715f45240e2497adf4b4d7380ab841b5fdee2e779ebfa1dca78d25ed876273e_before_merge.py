    def get_dataset(self, key, info):
        """Load a dataset."""
        if key.name not in self.datasets:
            return

        if self.nc is None:
            self.nc = xr.open_dataset(self.filename,
                                      decode_cf=True,
                                      mask_and_scale=True,
                                      engine='h5netcdf',
                                      chunks={'tie_columns': CHUNK_SIZE,
                                              'tie_rows': CHUNK_SIZE})

            self.nc = self.nc.rename({'tie_columns': 'x', 'tie_rows': 'y'})
        logger.debug('Reading %s.', key.name)

        l_step = self.nc.attrs['al_subsampling_factor']
        c_step = self.nc.attrs['ac_subsampling_factor']

        if (c_step != 1 or l_step != 1) and self.cache.get(key.name) is None:

            if key.name.startswith('satellite'):
                zen = self.nc[self.datasets['satellite_zenith_angle']]
                zattrs = zen.attrs
                azi = self.nc[self.datasets['satellite_azimuth_angle']]
                aattrs = azi.attrs
            elif key.name.startswith('solar'):
                zen = self.nc[self.datasets['solar_zenith_angle']]
                zattrs = zen.attrs
                azi = self.nc[self.datasets['solar_azimuth_angle']]
                aattrs = azi.attrs
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
            satint = Interpolator([x.values, y.values, z.values],
                                  (tie_lines, tie_cols),
                                  (lines, cols),
                                  along_track_order,
                                  cross_track_order)
            (x, y, z, ) = satint.interpolate()
            del satint
            x = xr.DataArray(da.from_array(x, chunks=(CHUNK_SIZE, CHUNK_SIZE)),
                             dims=['y', 'x'])
            y = xr.DataArray(da.from_array(y, chunks=(CHUNK_SIZE, CHUNK_SIZE)),
                             dims=['y', 'x'])
            z = xr.DataArray(da.from_array(z, chunks=(CHUNK_SIZE, CHUNK_SIZE)),
                             dims=['y', 'x'])

            azi, zen = xyz2angle(x, y, z)
            azi.attrs = aattrs
            zen.attrs = zattrs

            if 'zenith' in key.name:
                values = zen
            elif 'azimuth' in key.name:
                values = azi
            else:
                raise NotImplementedError("Don't know how to read " + key.name)

            if key.name.startswith('satellite'):
                self.cache['satellite_zenith_angle'] = zen
                self.cache['satellite_azimuth_angle'] = azi
            elif key.name.startswith('solar'):
                self.cache['solar_zenith_angle'] = zen
                self.cache['solar_azimuth_angle'] = azi

        elif key.name in self.cache:
            values = self.cache[key.name]
        else:
            values = self.nc[self.datasets[key.name]]

        values.attrs['platform_name'] = self.platform_name
        values.attrs['sensor'] = self.sensor

        values.attrs.update(key.to_dict())
        return values