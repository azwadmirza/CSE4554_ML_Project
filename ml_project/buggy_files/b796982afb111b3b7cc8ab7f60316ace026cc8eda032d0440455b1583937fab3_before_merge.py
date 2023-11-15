    def convert_to_radiance(self, data):
        """Calibrate to radiance."""
        coeffs = self.prologue["RadiometricProcessing"]
        coeffs = coeffs["Level1_5ImageCalibration"]
        gain = coeffs['Cal_Slope'][self.mda['spectral_channel_id'] - 1]
        offset = coeffs['Cal_Offset'][self.mda['spectral_channel_id'] - 1]

        data.data[:] *= gain
        data.data[:] += offset
        data.data[data.data < 0] = 0