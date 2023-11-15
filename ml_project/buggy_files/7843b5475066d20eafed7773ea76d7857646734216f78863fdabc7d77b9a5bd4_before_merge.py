    def transform(self, X):
        """Reduce X to the selected features.

        Parameters
        ----------
        X : array of shape [n_samples, n_features]
            The input samples.

        Returns
        -------
        X_r : array of shape [n_samples, n_selected_features]
            The input samples with only the selected features.
        """
        X = check_array(X, accept_sparse='csr')
        mask = self.get_support()
        if len(mask) != X.shape[1]:
            raise ValueError("X has a different shape than during fitting.")
        return check_array(X, accept_sparse='csr')[:, safe_mask(X, mask)]