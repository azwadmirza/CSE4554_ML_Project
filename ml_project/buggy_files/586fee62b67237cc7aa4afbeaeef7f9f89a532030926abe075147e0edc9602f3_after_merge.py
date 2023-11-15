    def _erads2bt(self, data):
        """computation based on effective radiance."""
        cal_info = CALIB[self.platform_id][self.channel_name]
        alpha = cal_info["ALPHA"]
        beta = cal_info["BETA"]
        wavenumber = cal_info["VC"]

        return mb.erads2bt(data, wavenumber, alpha, beta)