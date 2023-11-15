    def random(self, point=None, size=None, repeat=None):
        beta = draw_values([self.beta], point=point)[0]
        return generate_samples(self._random, beta,
                                dist_shape=self.shape,
                                size=size)