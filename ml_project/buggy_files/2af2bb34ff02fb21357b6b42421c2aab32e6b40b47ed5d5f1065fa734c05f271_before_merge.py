    def fit(self, X, y=None):
        """
        Compute the polynomial feature combinations
        """
        n_samples, n_features = check_array(X).shape
        self.powers_ = self._power_matrix(n_features, self.degree,
                                          self.interaction_only,
                                          self.include_bias)
        return self