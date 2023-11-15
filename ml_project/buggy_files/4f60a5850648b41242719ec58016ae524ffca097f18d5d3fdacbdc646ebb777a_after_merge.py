    def _vis_calibrate(self, data):
        """Visible channel calibration only."""
        solar_irradiance = CALIB[self.platform_id][self.channel_name]["F"]
        return mb.vis_calibrate(data, solar_irradiance)