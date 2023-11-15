    def forward(self, x):
        if x.ndimension() == 1:
            x = x.unsqueeze(-1)
        elif x.ndimension() != 2:
            raise RuntimeError("AdditiveGridInterpolationVariationalStrategy expects a 2d tensor.")

        num_data, num_dim = x.size()
        if num_dim != self.num_dim:
            raise RuntimeError("The number of dims should match the number specified.")

        output = super(AdditiveGridInterpolationVariationalStrategy, self).forward(x)
        if self.sum_output:
            mean = output.mean.sum(0)
            covar = output.lazy_covariance_matrix.sum(-3)
            return MultivariateNormal(mean, covar)
        else:
            return output