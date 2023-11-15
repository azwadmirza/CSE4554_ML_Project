    def _init_cache_for_non_constant_diag(self, eye, batch_shape, n):
        # With non-constant diagonals, we cant factor out the noise as easily
        self._q_cache, self._r_cache = torch.qr(torch.cat((self._piv_chol_self / self._noise.sqrt(), eye)))
        self._q_cache = self._q_cache[..., :n, :] / self._noise.sqrt()

        logdet = self._r_cache.diagonal(dim1=-1, dim2=-2).abs().log().sum(-1).mul(2)
        logdet -= (1.0 / self._noise).log().sum([-1, -2])
        self._precond_logdet_cache = logdet.view(*batch_shape) if len(batch_shape) else logdet.squeeze()