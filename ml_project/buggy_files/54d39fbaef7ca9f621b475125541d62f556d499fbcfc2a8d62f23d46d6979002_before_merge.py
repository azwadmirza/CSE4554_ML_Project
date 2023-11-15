    def _ir_calibrate(self, data):
        """IR calibration."""
        cal_type = self.prologue['ImageDescription'][
            'Level1_5ImageProduction']['PlannedChanProcessing'][self.mda['spectral_channel_id']]

        if cal_type == 1:
            # spectral radiances
            self._srads2bt(data)
        elif cal_type == 2:
            # effective radiances
            self._erads2bt(data)
        else:
            raise NotImplemented('Unknown calibration type')