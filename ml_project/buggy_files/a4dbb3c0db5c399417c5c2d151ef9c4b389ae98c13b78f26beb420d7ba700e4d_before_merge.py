    def _srads2bt(self, data, key_name):
        """computation based on spectral radiance."""
        coef_a, coef_b, coef_c = BTFIT[key_name]

        self._tl15(data, key_name)

        data.data[:] = (coef_a * data.data[:] ** 2 +
                        coef_b * data.data[:] +
                        coef_c)