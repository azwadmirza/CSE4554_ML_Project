    def _comp_samples(self, point=None, size=None):
        if self._comp_dists_vect or size is None:
            try:
                return self.comp_dists.random(point=point, size=size)
            except AttributeError:
                samples = np.array([comp_dist.random(point=point, size=size)
                                    for comp_dist in self.comp_dists])
                samples = np.moveaxis(samples, 0, samples.ndim - 1)
        else:
            # We must iterate the calls to random manually
            size = to_tuple(size)
            _size = int(np.prod(size))
            try:
                samples = np.array([self.comp_dists.random(point=point,
                                                           size=None)
                                    for _ in range(_size)])
                samples = np.reshape(samples, size + samples.shape[1:])
            except AttributeError:
                samples = np.array([[comp_dist.random(point=point, size=None)
                                     for _ in range(_size)]
                                    for comp_dist in self.comp_dists])
                samples = np.moveaxis(samples, 0, samples.ndim - 1)
                samples = np.reshape(samples, size + samples[1:])

        if samples.shape[-1] == 1:
            return samples[..., 0]
        else:
            return samples