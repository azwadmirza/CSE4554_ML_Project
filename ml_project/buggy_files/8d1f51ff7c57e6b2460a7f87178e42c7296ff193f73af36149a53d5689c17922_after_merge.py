    def __call__(self, x, prior=False):
        if not self.updated_strategy.item() and not prior:
            with torch.no_grad():
                # Get unwhitened p(u)
                prior_function_dist = self(self.inducing_points, prior=True)
                prior_mean = prior_function_dist.loc
                L = self._cholesky_factor(prior_function_dist.lazy_covariance_matrix.add_jitter())

                # Temporarily turn off noise that's added to the mean
                orig_mean_init_std = self._variational_distribution.mean_init_std
                self._variational_distribution.mean_init_std = 0.

                # Change the variational parameters to be whitened
                variational_dist = self.variational_distribution
                whitened_mean = torch.triangular_solve(
                    (variational_dist.loc - prior_mean).unsqueeze(-1).double(),
                    L, upper=False
                )[0].squeeze(-1).to(variational_dist.loc.dtype)
                whitened_covar = RootLazyTensor(torch.triangular_solve(
                    variational_dist.lazy_covariance_matrix.root_decomposition().root.evaluate().double(),
                    L, upper=False
                )[0].to(variational_dist.loc.dtype))
                whitened_variational_distribution = variational_dist.__class__(whitened_mean, whitened_covar)
                self._variational_distribution.initialize_variational_distribution(whitened_variational_distribution)

                # Reset the random noise parameter of the model
                self._variational_distribution.mean_init_std = orig_mean_init_std

                # Reset the cache
                if hasattr(self, "_memoize_cache"):
                    delattr(self, "_memoize_cache")
                    self._memoize_cache = dict()

                # Mark that we have updated the variational strategy
                self.updated_strategy.fill_(True)

        return super().__call__(x, prior=prior)