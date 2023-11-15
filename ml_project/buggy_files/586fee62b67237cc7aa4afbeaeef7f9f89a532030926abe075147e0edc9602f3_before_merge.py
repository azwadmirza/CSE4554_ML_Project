    def _erads2bt(self, data):
        """computation based on effective radiance."""
        cal_info = CALIB[self.platform_id][self.channel_name]
        alpha = cal_info["ALPHA"]
        beta = cal_info["BETA"]

        self._tl15(data)

        data.data[:] -= beta
        data.data[:] /= alpha