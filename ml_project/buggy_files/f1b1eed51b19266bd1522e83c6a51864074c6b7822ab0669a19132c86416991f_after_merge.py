    def _repr_cov_params(self, dist=None):
        if dist is None:
            dist = self
        if self._cov_type == 'chol':
            chol = get_variable_name(self.chol_cov)
            return r'\mathit{{chol}}={}'.format(chol)
        elif self._cov_type == 'cov':
            cov = get_variable_name(self.cov)
            return r'\mathit{{cov}}={}'.format(cov)
        elif self._cov_type == 'tau':
            tau = get_variable_name(self.tau)
            return r'\mathit{{tau}}={}'.format(tau)