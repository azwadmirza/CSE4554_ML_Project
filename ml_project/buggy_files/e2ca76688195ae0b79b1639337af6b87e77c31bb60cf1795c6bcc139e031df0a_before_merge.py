    def get_dataset(self, key, info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        """Get the data  from the files."""
        res = super(HRITGOMSFileHandler, self).get_dataset(key, info, out,
                                                           xslice, yslice)

        if res is not None:
            out = res

        self.calibrate(out, key.calibration)
        out.info['units'] = info['units']
        out.info['standard_name'] = info['standard_name']
        out.info['platform_name'] = self.platform_name
        out.info['sensor'] = 'msu-gs'