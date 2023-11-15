    def random(self, point=None, size=None, repeat=None):
        def random_choice(*args, **kwargs):
            w = kwargs.pop('w')
            w /= w.sum(axis=-1, keepdims=True)
            k = w.shape[-1]

            if w.ndim > 1:
                return np.row_stack([np.random.choice(k, p=w_) for w_ in w])
            else:
                return np.random.choice(k, p=w, *args, **kwargs)

        w = draw_values([self.w], point=point)[0]

        w_samples = generate_samples(random_choice,
                                     w=w,
                                     broadcast_shape=w.shape[:-1] or (1,),
                                     dist_shape=self.shape,
                                     size=size).squeeze()
        comp_samples = self._comp_samples(point=point, size=size, repeat=repeat)

        if comp_samples.ndim > 1:
            return np.squeeze(comp_samples[np.arange(w_samples.size), w_samples])
        else:
            return np.squeeze(comp_samples[w_samples])