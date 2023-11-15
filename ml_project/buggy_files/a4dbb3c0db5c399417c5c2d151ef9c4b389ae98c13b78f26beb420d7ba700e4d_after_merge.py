    def _srads2bt(self, data, key_name):
        """computation based on spectral radiance."""
        coef_a, coef_b, coef_c = BTFIT[key_name]
        wavenumber = CALIB[self.platform_id][key_name]["VC"]

        return mb.srads2bt(data, wavenumber, coef_a, coef_b, coef_c)