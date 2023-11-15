    def get_dataset(self, key, info, out=None, xslice=None, yslice=None):
        """Get the dataset designated by *key*."""
        if key.name in ['solar_zenith_angle', 'solar_azimuth_angle',
                        'satellite_zenith_angle', 'satellite_azimuth_angle']:

            if key.name == 'solar_zenith_angle':
                var = self.sd.select('SolarZenith')
            if key.name == 'solar_azimuth_angle':
                var = self.sd.select('SolarAzimuth')
            if key.name == 'satellite_zenith_angle':
                var = self.sd.select('SensorZenith')
            if key.name == 'satellite_azimuth_angle':
                var = self.sd.select('SensorAzimuth')

            mask = var[:] == var._FillValue
            data = np.ma.masked_array(var[:] * var.scale_factor, mask=mask)
            return Dataset(data, id=key, **info)

        if key.name not in ['longitude', 'latitude']:
            return

        if (self.cache[key.resolution]['lons'] is None or
                self.cache[key.resolution]['lats'] is None):

            lons_id = DatasetID('longitude',
                                resolution=key.resolution)
            lats_id = DatasetID('latitude',
                                resolution=key.resolution)

            lons, lats = self.load(
                [lons_id, lats_id], interpolate=False, raw=True)
            if key.resolution != self.resolution:
                from geotiepoints.geointerpolator import GeoInterpolator
                lons, lats = self._interpolate([lons, lats],
                                               self.resolution,
                                               lons_id.resolution,
                                               GeoInterpolator)
                lons = np.ma.masked_invalid(np.ascontiguousarray(lons))
                lats = np.ma.masked_invalid(np.ascontiguousarray(lats))
            self.cache[key.resolution]['lons'] = lons
            self.cache[key.resolution]['lats'] = lats

        if key.name == 'latitude':
            return Dataset(self.cache[key.resolution]['lats'], id=key, **info)
        else:
            return Dataset(self.cache[key.resolution]['lons'], id=key, **info)