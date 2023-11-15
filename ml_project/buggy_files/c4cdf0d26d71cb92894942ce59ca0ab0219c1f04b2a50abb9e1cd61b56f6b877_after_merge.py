    def forward(self, x, inducing_points, inducing_values, variational_inducing_covar=None):
        if variational_inducing_covar is None:
            raise RuntimeError(
                "GridInterpolationVariationalStrategy is only compatible with Gaussian variational "
                f"distributions. Got ({self.variational_distribution.__class__.__name__}."
            )

        variational_distribution = self.variational_distribution

        # Get interpolations
        interp_indices, interp_values = self._compute_grid(x)

        # Compute test mean
        # Left multiply samples by interpolation matrix
        predictive_mean = left_interp(interp_indices, interp_values, inducing_values.unsqueeze(-1))
        predictive_mean = predictive_mean.squeeze(-1)

        # Compute test covar
        predictive_covar = InterpolatedLazyTensor(
            variational_distribution.lazy_covariance_matrix,
            interp_indices,
            interp_values,
            interp_indices,
            interp_values,
        )
        output = MultivariateNormal(predictive_mean, predictive_covar)
        return output