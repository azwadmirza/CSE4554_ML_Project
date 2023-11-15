    def _srads2bt(self, data):
        """computation based on spectral radiance."""
        coef_a, coef_b, coef_c = BTFIT[self.channel_name]
        wavenumber = CALIB[self.platform_id][self.channel_name]["VC"]

        return mb.srads2bt(data, wavenumber, coef_a, coef_b, coef_c)