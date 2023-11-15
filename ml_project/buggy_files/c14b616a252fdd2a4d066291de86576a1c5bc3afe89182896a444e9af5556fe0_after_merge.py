    def _critvals(self, n):
        """
        Rows of the table, linearly interpolated for given sample size

        Parameters
        ----------
        n : float
            sample size, second parameter of the table

        Returns
        -------
        critv : ndarray, 1d
            critical values (ppf) corresponding to a row of the table

        Notes
        -----
        This is used in two step interpolation, or if we want to know the
        critical values for all alphas for any sample size that we can obtain
        through interpolation
        """
        if n > self.max_size:
            if self.asymptotic is not None:
                cv = self.asymptotic(n)
            else:
                raise ValueError('n is above max(size) and no asymptotic '
                                 'distribtuion is provided')
        else:
            cv = ([p(n) for p in self.polyn])
            if n > self.min_nobs:
                w = (n - self.min_nobs) / (self.max_nobs - self.min_nobs)
                w = min(1.0, w)
                a_cv = self.asymptotic(n)
                cv = w * a_cv + (1 - w) * cv

        return cv