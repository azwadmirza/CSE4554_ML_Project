    def transform(self, X, y=None):
        """Transform data to polynomial features

        Parameters
        ----------
        X : array with shape [n_samples, n_features]
            The data to transform, row by row.

        Returns
        -------
        XP : np.ndarray shape [n_samples, NP]
            The matrix of features, where NP is the number of polynomial
            features generated from the combination of inputs.
        """
        check_is_fitted(self, 'powers_')

        X = check_array(X)
        n_samples, n_features = X.shape

        if n_features != self.powers_.shape[1]:
            raise ValueError("X shape does not match training shape")

        return (X[:, None, :] ** self.powers_).prod(-1)