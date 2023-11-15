    def random(self, point=None, size=None, repeat=None):
        p = draw_values([self.p], point=point)
        return generate_samples(np.random.geometric, p,
                                dist_shape=self.shape,
                                size=size)