    def random(self, point=None, size=None):
        with _DrawValuesContext() as draw_context:
            w = draw_values([self.w], point=point)[0]
            comp_tmp = self._comp_samples(point=point, size=None)
        if np.asarray(self.shape).size == 0:
            distshape = np.asarray(np.broadcast(w, comp_tmp).shape)[..., :-1]
        else:
            distshape = np.asarray(self.shape)

        # Normalize inputs
        w /= w.sum(axis=-1, keepdims=True)

        w_samples = generate_samples(random_choice,
                                     p=w,
                                     broadcast_shape=w.shape[:-1] or (1,),
                                     dist_shape=distshape,
                                     size=size).squeeze()
        if (size is None) or (distshape.size == 0):
            with draw_context:
                comp_samples = self._comp_samples(point=point, size=size)
            if comp_samples.ndim > 1:
                samples = np.squeeze(comp_samples[np.arange(w_samples.size), ..., w_samples])
            else:
                samples = np.squeeze(comp_samples[w_samples])
        else:
            if w_samples.ndim == 1:
                w_samples = np.reshape(np.tile(w_samples, size), (size,) + w_samples.shape)
            samples = np.zeros((size,)+tuple(distshape))
            with draw_context:
                for i in range(size):
                    w_tmp = w_samples[i, :]
                    comp_tmp = self._comp_samples(point=point, size=None)
                    if comp_tmp.ndim > 1:
                        samples[i, :] = np.squeeze(comp_tmp[np.arange(w_tmp.size), ..., w_tmp])
                    else:
                        samples[i, :] = np.squeeze(comp_tmp[w_tmp])

        return samples