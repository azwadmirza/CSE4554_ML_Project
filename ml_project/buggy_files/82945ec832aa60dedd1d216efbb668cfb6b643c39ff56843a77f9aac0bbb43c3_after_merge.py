    def _init_cache(self):
        *batch_shape, n, k = self._piv_chol_self.shape
        self._noise = self._diag_tensor.diag().unsqueeze(-1)

        # the check for constant diag needs to be done carefully for batches.
        noise_first_element = self._noise[..., :1, :]
        self._constant_diag = torch.equal(self._noise, noise_first_element * torch.ones_like(self._noise))
        eye = torch.eye(k, dtype=self._piv_chol_self.dtype, device=self._piv_chol_self.device)
        eye = eye.expand(*batch_shape, k, k)

        if self._constant_diag:
            self._init_cache_for_constant_diag(eye, batch_shape, n, k)
        else:
            self._init_cache_for_non_constant_diag(eye, batch_shape, n)

        self._precond_lt = PsdSumLazyTensor(RootLazyTensor(self._piv_chol_self), self._diag_tensor)