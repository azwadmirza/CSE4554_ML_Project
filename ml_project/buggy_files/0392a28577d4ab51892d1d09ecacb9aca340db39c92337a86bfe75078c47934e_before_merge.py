    def get_dataset(self, key, info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        res = super(HRITMSGFileHandler, self).get_dataset(key, info, out,
                                                          xslice, yslice)
        if res is not None:
            out = res

        self.calibrate(out, key.calibration)

        out.info['units'] = info['units']
        out.info['wavelength'] = info['wavelength']
        out.info['standard_name'] = info['standard_name']
        out.info['platform_name'] = self.platform_name
        out.info['sensor'] = 'seviri'
        out.info['satellite_longitude'] = self.mda[
            'projection_parameters']['SSP_longitude']
        out.info['satellite_latitude'] = self.mda[
            'projection_parameters']['SSP_latitude']
        out.info['satellite_altitude'] = self.mda['projection_parameters']['h']