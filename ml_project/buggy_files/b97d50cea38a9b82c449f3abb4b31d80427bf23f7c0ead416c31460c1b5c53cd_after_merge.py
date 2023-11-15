    def forward(self, x1, x2):
        batch_size, n, num_dims = x1.size()
        _, m, _ = x2.size()

        if not num_dims == self.ard_num_dims:
            raise RuntimeError(
                "The SpectralMixtureKernel expected the input to have {} dimensionality "
                "(based on the ard_num_dims argument). Got {}.".format(self.ard_num_dims, num_dims)
            )
        if not batch_size == self.batch_size:
            raise RuntimeError(
                "The SpectralMixtureKernel expected the input to have a batch_size of {} "
                "(based on the batch_size argument). Got {}.".format(self.batch_size, batch_size)
            )

        # Expand x1 and x2 to account for the number of mixtures
        # Should make x1/x2 (b x k x n x d) for k mixtures
        x1_ = x1.unsqueeze(1)
        x2_ = x2.unsqueeze(1)

        # Compute distances - scaled by appropriate parameters
        x1_exp = x1_ * self.mixture_scales
        x2_exp = x2_ * self.mixture_scales
        x1_cos = x1_ * self.mixture_means
        x2_cos = x2_ * self.mixture_means

        # Create grids
        x1_exp_, x2_exp_ = self._create_input_grid(x1_exp, x2_exp)
        x1_cos_, x2_cos_ = self._create_input_grid(x1_cos, x2_cos)

        # Compute the exponential and cosine terms
        exp_term = (x1_exp_ - x2_exp_).pow_(2).mul_(-2 * math.pi ** 2)
        cos_term = (x1_cos_ - x2_cos_).mul_(2 * math.pi)
        res = exp_term.exp_() * cos_term.cos_()

        # Product omer dimensions
        res = res.prod(-1)

        # Sum over mixtures
        mixture_weights = self.mixture_weights
        while mixture_weights.dim() < res.dim():
            mixture_weights.unsqueeze_(-1)
        res = (res * mixture_weights).sum(1)
        return res