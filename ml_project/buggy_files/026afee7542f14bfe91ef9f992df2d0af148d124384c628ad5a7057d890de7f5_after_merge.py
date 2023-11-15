    def calibrate(self, data, calibration):
        """Calibrate the data."""
        tic = datetime.now()

        if calibration == 'counts':
            res = data

        if calibration in ['radiance', 'brightness_temperature']:
            res = self._calibrate(data)
        else:
            raise NotImplementedError("Don't know how to calibrate to " +
                                      str(calibration))

        res.attrs['standard_name'] = calibration
        res.attrs['calibration'] = calibration

        logger.debug("Calibration time " + str(datetime.now() - tic))
        return res