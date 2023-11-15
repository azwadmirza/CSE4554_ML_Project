    def random(self, point=None, size=None, repeat=None):
        mu = draw_values([self.mu], point=point)[0]
        return generate_samples(stats.poisson.rvs, mu,
                                dist_shape=self.shape,
                                size=size)