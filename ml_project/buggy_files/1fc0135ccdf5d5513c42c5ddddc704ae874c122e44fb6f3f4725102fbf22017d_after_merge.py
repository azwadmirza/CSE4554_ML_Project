    def get_n_splits(self, X, y, groups):
        """Returns the number of splitting iterations in the cross-validator

        Parameters
        ----------
        X : object
            Always ignored, exists for compatibility.
            ``np.zeros(n_samples)`` may be used as a placeholder.

        y : object
            Always ignored, exists for compatibility.
            ``np.zeros(n_samples)`` may be used as a placeholder.

        groups : array-like, with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into
            train/test set.

        Returns
        -------
        n_splits : int
            Returns the number of splitting iterations in the cross-validator.
        """
        if groups is None:
            raise ValueError("The groups parameter should not be None")
        groups = check_array(groups, ensure_2d=False, dtype=None)
        X, y, groups = indexable(X, y, groups)
        return int(comb(len(np.unique(groups)), self.n_groups, exact=True))