    def _comp_samples(self, point=None, size=None):
        try:
            samples = self.comp_dists.random(point=point, size=size)
        except AttributeError:
            samples = np.column_stack([comp_dist.random(point=point, size=size)
                                       for comp_dist in self.comp_dists])

        return np.squeeze(samples)