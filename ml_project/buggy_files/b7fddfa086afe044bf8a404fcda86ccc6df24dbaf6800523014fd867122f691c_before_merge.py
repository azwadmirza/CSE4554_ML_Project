    def setup_nominal(self, endog, exog, groups, time, offset):
        """
        Restructure nominal data as binary indicators so that they can
        be analysed using Generalized Estimating Equations.
        """

        self.endog_orig = endog.copy()
        self.exog_orig = exog.copy()
        self.groups_orig = groups.copy()
        if offset is not None:
            self.offset_orig = offset.copy()
        else:
            self.offset_orig = None
            offset = np.zeros(len(endog))
        if time is not None:
            self.time_orig = time.copy()
        else:
            self.time_orig = None
            time = np.zeros((len(endog),1))

        # The unique outcomes, except the greatest one.
        self.endog_values = np.unique(endog)
        endog_cuts = self.endog_values[0:-1]
        ncut = len(endog_cuts)

        nrows = len(endog_cuts) * exog.shape[0]
        ncols = len(endog_cuts) * exog.shape[1]
        exog_out = np.zeros((nrows, ncols), dtype=np.float64)
        endog_out = np.zeros(nrows, dtype=np.float64)
        groups_out = np.zeros(nrows, dtype=np.float64)
        time_out = np.zeros((nrows, time.shape[1]),
                        dtype=np.float64)
        offset_out = np.zeros(nrows, dtype=np.float64)

        jrow = 0
        zipper = zip(exog, endog, groups, time, offset)
        for (exog_row, endog_value, group_value, time_value,
             offset_value) in zipper:

            # Loop over thresholds for the indicators
            for thresh_ix, thresh in enumerate(endog_cuts):

                u = np.zeros(len(endog_cuts), dtype=np.float64)
                u[thresh_ix] = 1
                exog_out[jrow, :] = np.kron(u, exog_row)
                endog_out[jrow] = (int(endog_value == thresh))
                groups_out[jrow] = group_value
                time_out[jrow] = time_value
                offset_out[jrow] = offset_value
                jrow += 1

        # exog names
        if type(self.exog_orig) == pd.DataFrame:
            xnames_in = self.exog_orig.columns
        else:
            xnames_in = ["x%d" % k for k in range(1, exog.shape[1]+1)]
        xnames = []
        for tr in endog_cuts:
            xnames.extend(["%s[%.1f]" % (v, tr) for v in xnames_in])
        exog_out = pd.DataFrame(exog_out, columns=xnames)
        exog_out = pd.DataFrame(exog_out, columns=xnames)

        # Preserve endog name if there is one
        if type(self.endog_orig) == pd.Series:
            endog_out = pd.Series(endog_out, name=self.endog_orig.names)

        return endog_out, exog_out, groups_out, time_out, offset_out