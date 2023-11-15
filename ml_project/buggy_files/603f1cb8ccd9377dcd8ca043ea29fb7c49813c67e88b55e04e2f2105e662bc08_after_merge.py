    def random(self, point=None, size=None):
        if size is None:
            size = tuple()
        else:
            if not isinstance(size, tuple):
                try:
                    size = tuple(size)
                except TypeError:
                    size = (size,)

        if self._cov_type == 'cov':
            mu, cov = draw_values([self.mu, self.cov], point=point, size=size)
            if mu.shape[-1] != cov.shape[-1]:
                raise ValueError("Shapes for mu and cov don't match")

            try:
                dist = stats.multivariate_normal(
                    mean=mu, cov=cov, allow_singular=True)
            except ValueError:
                size += (mu.shape[-1],)
                return np.nan * np.zeros(size)
            return dist.rvs(size)
        elif self._cov_type == 'chol':
            mu, chol = draw_values([self.mu, self.chol_cov],
                                   point=point, size=size)
            if size and mu.ndim == len(size) and mu.shape == size:
                mu = mu[..., np.newaxis]
            if mu.shape[-1] != chol.shape[-1] and mu.shape[-1] != 1:
                raise ValueError("Shapes for mu and chol don't match")
            broadcast_shape = (
                np.broadcast(np.empty(mu.shape[:-1]),
                             np.empty(chol.shape[:-2])).shape
            )

            mu = np.broadcast_to(mu, broadcast_shape + (chol.shape[-1],))
            chol = np.broadcast_to(chol, broadcast_shape + chol.shape[-2:])
            # If mu and chol were fixed by the point, only the standard normal
            # should change
            if mu.shape[:len(size)] != size:
                std_norm_shape = size + mu.shape
            else:
                std_norm_shape = mu.shape
            standard_normal = np.random.standard_normal(std_norm_shape)
            return mu + np.tensordot(standard_normal, chol, axes=[[-1], [-1]])
        else:
            mu, tau = draw_values([self.mu, self.tau], point=point, size=size)
            if mu.shape[-1] != tau[0].shape[-1]:
                raise ValueError("Shapes for mu and tau don't match")

            size += (mu.shape[-1],)
            try:
                chol = linalg.cholesky(tau, lower=True)
            except linalg.LinAlgError:
                return np.nan * np.zeros(size)

            standard_normal = np.random.standard_normal(size)
            transformed = linalg.solve_triangular(
                chol, standard_normal.T, lower=True)
            return mu + transformed.T