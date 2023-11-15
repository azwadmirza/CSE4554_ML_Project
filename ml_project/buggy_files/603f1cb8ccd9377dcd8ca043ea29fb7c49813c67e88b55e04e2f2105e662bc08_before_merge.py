    def random(self, point=None, size=None):
        if size is None:
            size = []
        else:
            try:
                size = list(size)
            except TypeError:
                size = [size]

        if self._cov_type == 'cov':
            mu, cov = draw_values([self.mu, self.cov], point=point, size=size)
            if mu.shape[-1] != cov.shape[-1]:
                raise ValueError("Shapes for mu and cov don't match")

            try:
                dist = stats.multivariate_normal(
                    mean=mu, cov=cov, allow_singular=True)
            except ValueError:
                size.append(mu.shape[-1])
                return np.nan * np.zeros(size)
            return dist.rvs(size)
        elif self._cov_type == 'chol':
            mu, chol = draw_values([self.mu, self.chol_cov], point=point, size=size)
            if mu.shape[-1] != chol[0].shape[-1]:
                raise ValueError("Shapes for mu and chol don't match")

            size.append(mu.shape[-1])
            standard_normal = np.random.standard_normal(size)
            return mu + np.dot(standard_normal, chol.T)
        else:
            mu, tau = draw_values([self.mu, self.tau], point=point, size=size)
            if mu.shape[-1] != tau[0].shape[-1]:
                raise ValueError("Shapes for mu and tau don't match")

            size.append(mu.shape[-1])
            try:
                chol = linalg.cholesky(tau, lower=True)
            except linalg.LinAlgError:
                return np.nan * np.zeros(size)

            standard_normal = np.random.standard_normal(size)
            transformed = linalg.solve_triangular(
                chol, standard_normal.T, lower=True)
            return mu + transformed.T