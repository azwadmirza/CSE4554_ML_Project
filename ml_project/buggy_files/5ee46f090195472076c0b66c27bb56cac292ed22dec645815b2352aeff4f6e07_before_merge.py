    def summary2(self, alpha=0.05, float_format="%.4f"):
        """Experimental function to summarize regression results

        Parameters
        -----------
        alpha : float
            significance level for the confidence intervals
        float_format: string
            print format for floats in parameters summary

        Returns
        -------
        smry : Summary instance
            this holds the summary tables and text, which can be printed or
            converted to various output formats.

        See Also
        --------
        statsmodels.iolib.summary2.Summary : class to hold summary
            results

        """

        from statsmodels.iolib import summary2
        smry = summary2.Summary()
        smry.add_dict(summary2.summary_model(self))
        # One data frame per value of endog
        eqn = self.params.shape[1]
        confint = self.conf_int(alpha)
        for i in range(eqn):
            coefs = summary2.summary_params(self, alpha, self.params[:,i],
                    self.bse[:,i], self.tvalues[:,i], self.pvalues[:,i],
                    confint[i])
            # Header must show value of endog
            level_str =  self.model.endog_names + ' = ' + str(i)
            coefs[level_str] = coefs.index
            coefs = coefs.iloc[:,[-1,0,1,2,3,4,5]]
            smry.add_df(coefs, index=False, header=True, float_format=float_format)
            smry.add_title(results=self)
        return smry