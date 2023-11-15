    def calibrate(self, data, key):
        """Data calibration.
        """

#        logger.debug('Calibration: %s' % key.calibration)
        logger.warning('Calibration disabled!')
        if key.calibration == 'brightness_temperature':
            pass
#            self._ir_calibrate(data, key)
        elif key.calibration == 'reflectance':
            pass
#            self._vis_calibrate(data, key)
        else:
            pass

        return(data)