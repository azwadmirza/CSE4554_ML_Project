    def calibrate(self, data):
        """Calibrate the data."""
        logger.debug("Calibrate")

        ch = int(self.nc["band_id"])

        if ch < 7:
            return self._vis_calibrate(data)
        else:
            return self._ir_calibrate(data)