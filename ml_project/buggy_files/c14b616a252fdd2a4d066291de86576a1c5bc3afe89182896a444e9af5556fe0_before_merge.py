    def _critvals(self, n):
        '''rows of the table, linearly interpolated for given sample size

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

        '''
        return np.array([p(n) for p in self.polyn])