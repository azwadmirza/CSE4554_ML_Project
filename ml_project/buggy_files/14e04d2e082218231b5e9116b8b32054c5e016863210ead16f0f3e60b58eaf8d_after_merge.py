    def _erads2bt(self, data, key_name):
        """computation based on effective radiance."""
        cal_info = CALIB[self.platform_id][key_name]
        alpha = cal_info["ALPHA"]
        beta = cal_info["BETA"]
        wavenumber = CALIB[self.platform_id][key_name]["VC"]

        return mb.erads2bt(data, wavenumber, alpha, beta)