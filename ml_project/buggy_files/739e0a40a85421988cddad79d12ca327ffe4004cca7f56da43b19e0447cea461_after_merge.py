    def random(self, point=None, size=None):
        a = draw_values([self.a], point=point)[0]

        def _random(a, size=None):
            return stats.dirichlet.rvs(a, None if size == a.shape else size)

        samples = generate_samples(_random, a,
                                   dist_shape=self.shape,
                                   size=size)
        return samples