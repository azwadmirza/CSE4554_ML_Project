    def forward(self, x1, x2):
        batch_size, n, n_dims = x1.size()
        _, m, _ = x2.size()
        if not n_dims == self.n_dims:
            raise RuntimeError("The number of dimensions doesn't match what was supplied!")

        mixture_weights = self.log_mixture_weights.view(self.n_mixtures, 1, 1, 1).exp()
        mixture_means = self.log_mixture_means.view(self.n_mixtures, 1, 1, 1, self.n_dims).exp()
        mixture_scales = self.log_mixture_scales.view(self.n_mixtures, 1, 1, 1, self.n_dims).exp()
        distance = (x1.unsqueeze(-2) - x2.unsqueeze(-3)).abs()  # distance = x^(i) - z^(i)

        exp_term = (distance * mixture_scales).pow_(2).mul_(-2 * math.pi ** 2)
        cos_term = (distance * mixture_means).mul_(2 * math.pi)
        res = exp_term.exp_() * cos_term.cos_()

        # Product over dimensions
        res = res.prod(-1)

        # Sum over mixtures
        res = (res * mixture_weights).sum(0)
        return res