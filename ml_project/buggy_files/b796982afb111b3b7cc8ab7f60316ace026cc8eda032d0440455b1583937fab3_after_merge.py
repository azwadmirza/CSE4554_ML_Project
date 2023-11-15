    def convert_to_radiance(self, data):
        """Calibrate to radiance."""
        coeffs = self.prologue["RadiometricProcessing"]
        coeffs = coeffs["Level1_5ImageCalibration"]
        gain = coeffs['Cal_Slope'][self.mda['spectral_channel_id'] - 1]
        offset = coeffs['Cal_Offset'][self.mda['spectral_channel_id'] - 1]

        return mb.convert_to_radiance(data, gain, offset)