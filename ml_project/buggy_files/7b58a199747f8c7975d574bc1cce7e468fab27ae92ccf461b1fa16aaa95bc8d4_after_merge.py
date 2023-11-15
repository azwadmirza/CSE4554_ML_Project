    def _vis_calibrate(self, data, key_name):
        """Visible channel calibration only."""
        solar_irradiance = CALIB[self.platform_id][key_name]["F"]
        return mb.vis_calibrate(data, solar_irradiance)