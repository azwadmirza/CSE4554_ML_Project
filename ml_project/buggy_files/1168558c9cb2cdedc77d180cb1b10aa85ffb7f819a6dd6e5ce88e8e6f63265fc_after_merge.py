    def calibrate(self, data, calibration):
        """Calibrate the data."""
        tic = datetime.now()
        if calibration == 'counts':
            res = data
        elif calibration in ['radiance', 'reflectance', 'brightness_temperature']:
            res = self.convert_to_radiance(data)
        if calibration == 'reflectance':
            res = self._vis_calibrate(res)
        elif calibration == 'brightness_temperature':
            res = self._ir_calibrate(res)

        logger.debug("Calibration time " + str(datetime.now() - tic))
        return res