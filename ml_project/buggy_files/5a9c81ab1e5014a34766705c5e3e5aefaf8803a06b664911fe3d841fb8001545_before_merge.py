    def stderr(self):
        """Standard errors of coefficients, reshaped to match in size
        """
        stderr = np.sqrt(np.diag(self._cov_params()))
        return stderr.reshape((self.df_model, self.neqs), order='C')