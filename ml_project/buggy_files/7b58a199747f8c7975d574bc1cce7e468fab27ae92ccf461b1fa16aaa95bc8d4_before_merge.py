    def _vis_calibrate(self, data, key_name):
        """Visible channel calibration only."""
        solar_irradiance = CALIB[self.platform_id][key_name]["F"]
        data.data[:] *= 100 / solar_irradiance