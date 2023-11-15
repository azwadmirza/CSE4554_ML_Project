    def forward(self, x, inducing_points, inducing_values, variational_inducing_covar=None):
        if x.ndimension() == 1:
            x = x.unsqueeze(-1)
        elif x.ndimension() != 2:
            raise RuntimeError("AdditiveGridInterpolationVariationalStrategy expects a 2d tensor.")

        num_data, num_dim = x.size()
        if num_dim != self.num_dim:
            raise RuntimeError("The number of dims should match the number specified.")

        output = super().forward(x, inducing_points, inducing_values, variational_inducing_covar)
        if self.sum_output:
            if variational_inducing_covar is not None:
                mean = output.mean.sum(0)
                covar = output.lazy_covariance_matrix.sum(-3)
                return MultivariateNormal(mean, covar)
            else:
                return Delta(output.mean.sum(0))
        else:
            return output