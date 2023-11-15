    def reweight_covariance(self, data):
        """Re-weight raw Minimum Covariance Determinant estimates.

        Re-weight observations using Rousseeuw's method (equivalent to
        deleting outlying observations from the data set before
        computing location and covariance estimates). [Rouseeuw1984]_

        Parameters
        ----------
        data : array-like, shape (n_samples, n_features)
            The data matrix, with p features and n samples.
            The data set must be the one which was used to compute
            the raw estimates.

        Returns
        -------
        location_reweighted : array-like, shape (n_features, )
            Re-weighted robust location estimate.

        covariance_reweighted : array-like, shape (n_features, n_features)
            Re-weighted robust covariance estimate.

        support_reweighted : array-like, type boolean, shape (n_samples,)
            A mask of the observations that have been used to compute
            the re-weighted robust location and covariance estimates.

        """
        n_samples, n_features = data.shape
        mask = self.dist_ < chi2(n_features).isf(0.025)
        if self.assume_centered:
            location_reweighted = np.zeros(n_features)
        else:
            location_reweighted = data[mask].mean(0)
        covariance_reweighted = self._nonrobust_covariance(
            data[mask], assume_centered=self.assume_centered)
        support_reweighted = np.zeros(n_samples, dtype=bool)
        support_reweighted[mask] = True
        self._set_covariance(covariance_reweighted)
        self.location_ = location_reweighted
        self.support_ = support_reweighted
        X_centered = data - self.location_
        self.dist_ = np.sum(
            np.dot(X_centered, self.get_precision()) * X_centered, 1)
        return location_reweighted, covariance_reweighted, support_reweighted