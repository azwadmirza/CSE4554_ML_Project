    def inverse_transform(self, X):
        """Scale back the data to the original representation. Multiplies by
        the scale found in :meth:`fit`.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features, 3)
            Data to apply the inverse transform to, c.f. :meth:`transform`.

        Returns
        -------
        Xs : ndarray of shape (n_samples, n_features, 3)
            Rescaled diagrams.

        """
        check_is_fitted(self)

        Xs = check_diagrams(X)
        Xs[:, :, :2] *= self.scale_
        return Xs