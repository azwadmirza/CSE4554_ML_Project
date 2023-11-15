    def get_dataset(self, key, info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        """Get the data  from the files."""
        res = super(HRITGOMSFileHandler, self).get_dataset(key, info)

        res = self.calibrate(res, key.calibration)
        res.attrs['units'] = info['units']
        res.attrs['standard_name'] = info['standard_name']
        res.attrs['platform_name'] = self.platform_name
        res.attrs['sensor'] = 'msu-gs'
        res.attrs['satellite_longitude'] = self.mda['projection_parameters']['SSP_longitude']
        res.attrs['satellite_latitude'] = 0
        res.attrs['satellite_altitude'] = 35785831.00

        return res