    def sample(
        self, num_samples: Optional[int] = None, dtype=np.float32
    ) -> Tensor:
        F = self.F
        samples_list = [c.sample(num_samples, dtype) for c in self.components]
        samples = F.stack(*samples_list, axis=-1)

        mixture_probs = _expand_param(self.mixture_probs, num_samples)

        idx = F.random.multinomial(mixture_probs)

        n_axes = len(samples_list[0].shape)
        for _ in range(n_axes - len(idx.shape)):
            idx = idx.expand_dims(axis=-1)
        idx = idx.broadcast_to(samples_list[0].shape)

        selected_samples = F.pick(data=samples, index=idx, axis=-1)

        return selected_samples