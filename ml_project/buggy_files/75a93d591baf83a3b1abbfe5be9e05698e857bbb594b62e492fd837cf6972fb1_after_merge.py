    def _ir_calibrate(self, data, key_name):
        """IR calibration."""

        channel_index = self.channel_order_list.index(key_name)

        cal_type = self.header['15_DATA_HEADER']['ImageDescription'][
            'Level15ImageProduction']['PlannedChanProcessing'][0][channel_index]

        if cal_type == 1:
            # spectral radiances
            return self._srads2bt(data, key_name)
        elif cal_type == 2:
            # effective radiances
            return self._erads2bt(data, key_name)
        else:
            raise NotImplementedError('Unknown calibration type')