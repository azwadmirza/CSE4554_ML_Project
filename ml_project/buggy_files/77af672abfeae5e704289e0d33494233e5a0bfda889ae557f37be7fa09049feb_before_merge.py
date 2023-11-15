    def calibrate(self, data, key):
        """Calibrate the data."""
        tic = datetime.now()

        calibration = key.calibration
        if calibration == 'counts':
            return

        if calibration in ['radiance', 'reflectance', 'brightness_temperature']:
            self.convert_to_radiance(data, key.name)
        if calibration == 'reflectance':
            self._vis_calibrate(data, key.name)
        elif calibration == 'brightness_temperature':
            self._ir_calibrate(data, key.name)

        logger.debug("Calibration time " + str(datetime.now() - tic))