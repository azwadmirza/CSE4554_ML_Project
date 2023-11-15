    def sample(
        self, num_samples: Optional[int] = None, dtype=np.float32
    ) -> Tensor:
        F = self.F
        samples_list = [c.sample(num_samples, dtype) for c in self.components]
        samples = F.stack(*samples_list, axis=-1)

        mixture_probs = _expand_param(self.mixture_probs, num_samples)

        idx = F.random.multinomial(mixture_probs)

        for _ in range(self.event_dim):
            idx = idx.expand_dims(axis=-1)
        idx = idx.broadcast_like(samples_list[0])

        selected_samples = F.pick(data=samples, index=idx, axis=-1)

        return selected_samples