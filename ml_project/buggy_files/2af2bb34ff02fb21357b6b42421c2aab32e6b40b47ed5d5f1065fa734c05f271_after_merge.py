    def fit(self, X, y=None):
        """
        Compute number of output features.
        """
        n_samples, n_features = check_array(X).shape
        combinations = self._combinations(n_features, self.degree,
                                          self.interaction_only,
                                          self.include_bias)
        self.n_input_features_ = n_features
        self.n_output_features_ = sum(1 for _ in combinations)
        return self