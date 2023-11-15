    def calibrate(self, data, key):
        """Calibrate the data."""
        tic = datetime.now()

        calibration = key.calibration
        if calibration == 'counts':
            return

        if calibration in ['radiance', 'reflectance', 'brightness_temperature']:
            res = self.convert_to_radiance(data, key.name)
        if calibration == 'reflectance':
            res = self._vis_calibrate(res, key.name)
        elif calibration == 'brightness_temperature':
            res = self._ir_calibrate(res, key.name)

        logger.debug("Calibration time " + str(datetime.now() - tic))

        return res