    def convert_to_radiance(self, data, key_name):
        """Calibrate to radiance."""

        coeffs = self.header['15_DATA_HEADER'][
            'RadiometricProcessing']['Level15ImageCalibration']

        channel_index = self.channel_order_list.index(key_name)

        gain = coeffs['CalSlope'][0][channel_index]
        offset = coeffs['CalOffset'][0][channel_index]

        return mb.convert_to_radiance(data, gain, offset)