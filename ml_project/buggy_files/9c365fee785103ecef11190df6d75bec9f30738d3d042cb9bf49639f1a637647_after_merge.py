    def random(self, point=None, size=None, repeat=None):
        p = draw_values([self.p], point=point)[0]
        return generate_samples(stats.bernoulli.rvs, p,
                                dist_shape=self.shape,
                                size=size)