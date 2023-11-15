    def summary(self, xname=None, alpha=0.05, title=None):
        """Summarize the Results of the hypothesis test

        Parameters
        -----------

        xname : list of strings, optional
            Default is `c_##` for ## in p the number of regressors
        alpha : float
            significance level for the confidence intervals. Default is
            alpha = 0.05 which implies a confidence level of 95%.
        title : string, optional
            Title for the params table. If not None, then this replaces the
            default title

        Returns
        -------
        smry : string or Summary instance
            This contains a parameter results table in the case of t or z test
            in the same form as the parameter results table in the model
            results summary.
            For F or Wald test, the return is a string.

        """
        if self.effect is not None:
            # TODO: should also add some extra information, e.g. robust cov ?
            # TODO: can we infer names for constraints, xname in __init__ ?
            if title is None:
                title = 'Test for Constraints'
            elif title == '':
                # don't add any title,
                # I think SimpleTable skips on None - check
                title = None
            # we have everything for a params table
            use_t = (self.distribution == 't')
            yname='constraints' # Not used in params_frame
            if xname is None:
                xname = ['c%d'%ii for ii in range(len(self.effect))]
            from statsmodels.iolib.summary import summary_params
            pvalues = np.atleast_1d(self.pvalue)
            summ = summary_params((self, self.effect, self.sd, self.statistic,
                                   pvalues, self.conf_int(alpha)),
                                  yname=yname, xname=xname, use_t=use_t,
                                  title=title, alpha=alpha)
            return summ
        elif hasattr(self, 'fvalue'):
            # TODO: create something nicer for these casee
            return '<F test: F=%s, p=%s, df_denom=%d, df_num=%d>' % \
                   (repr(self.fvalue), self.pvalue, self.df_denom, self.df_num)
        elif self.distribution == 'chi2':
            return '<Wald test (%s): statistic=%s, p-value=%s, df_denom=%d>' % \
                   (self.distribution, self.statistic, self.pvalue, self.df_denom)
        else:
            # generic
            return '<Wald test: statistic=%s, p-value=%s>' % \
                   (self.statistic, self.pvalue)