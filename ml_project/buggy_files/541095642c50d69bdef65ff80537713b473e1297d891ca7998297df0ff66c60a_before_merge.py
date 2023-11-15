    def transform(self, X, ridge_alpha=None):
        """Least Squares projection of the data onto the sparse components.

        To avoid instability issues in case the system is under-determined,
        regularization can be applied (Ridge regression) via the
        `ridge_alpha` parameter.

        Note that Sparse PCA components orthogonality is not enforced as in PCA
        hence one cannot use a simple linear projection.

        Parameters
        ----------
        X: array of shape (n_samples, n_features)
            Test data to be transformed, must have the same number of
            features as the data used to train the model.

        ridge_alpha: float, default: 0.01
            Amount of ridge shrinkage to apply in order to improve
            conditioning.

        Returns
        -------
        X_new array, shape (n_samples, n_components)
            Transformed data.
        """
        ridge_alpha = self.ridge_alpha if ridge_alpha is None else ridge_alpha
        U = ridge_regression(self.components_.T, X.T, ridge_alpha,
                             solver='dense_cholesky')
        s = np.sqrt((U ** 2).sum(axis=0))
        s[s == 0] = 1
        U /= s
        return U