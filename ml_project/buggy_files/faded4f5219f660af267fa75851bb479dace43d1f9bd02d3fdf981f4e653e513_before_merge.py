    def _srads2bt(self, data):
        """computation based on spectral radiance."""
        coef_a, coef_b, coef_c = BTFIT[self.channel_name]

        self._tl15(data)

        data.data[:] = (coef_a * data.data[:] ** 2 +
                        coef_b * data.data[:] +
                        coef_c)