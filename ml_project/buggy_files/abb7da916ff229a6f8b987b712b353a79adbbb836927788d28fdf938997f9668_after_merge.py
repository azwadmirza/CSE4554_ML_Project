    def random(self, point=None, size=None, repeat=None):
        c = draw_values([self.c], point=point)[0]
        dtype = np.array(c).dtype

        def _random(c, dtype=dtype, size=None):
            return np.full(size, fill_value=c, dtype=dtype)

        return generate_samples(_random, c=c, dist_shape=self.shape,
                                size=size).astype(dtype)