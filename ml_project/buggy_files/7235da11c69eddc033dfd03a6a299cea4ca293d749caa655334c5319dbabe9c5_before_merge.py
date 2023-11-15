    def random(self, point=None, size=None, repeat=None):
        sd = draw_values([self.sd], point=point)
        return generate_samples(stats.halfnorm.rvs, loc=0., scale=sd,
                                dist_shape=self.shape,
                                size=size)