    def __init__(self, t=None, F=None, sd=None, effect=None, df_denom=None,
                 df_num=None, alpha=0.05, **kwds):

        self.effect = effect  # Let it be None for F
        if F is not None:
            self.distribution = 'F'
            self.fvalue = F
            self.statistic = self.fvalue
            self.df_denom = df_denom
            self.df_num = df_num
            self.dist = fdist
            self.dist_args = (df_num, df_denom)
            self.pvalue = fdist.sf(F, df_num, df_denom)
        elif t is not None:
            self.distribution = 't'
            self.tvalue = t
            self.statistic = t  # generic alias
            self.sd = sd
            self.df_denom = df_denom
            self.dist = student_t
            self.dist_args = (df_denom,)
            self.pvalue = self.dist.sf(np.abs(t), df_denom) * 2
        elif 'statistic' in kwds:
            # TODO: currently targeted to normal distribution, and chi2
            self.distribution = kwds['distribution']
            self.statistic = kwds['statistic']
            self.tvalue = value = kwds['statistic']  # keep alias
            # TODO: for results instance we decided to use tvalues also for normal
            self.sd = sd
            self.dist = getattr(stats, self.distribution)
            self.dist_args = ()
            if self.distribution is 'chi2':
                self.pvalue = self.dist.sf(self.statistic, df_denom)
            else:
                "normal"
                self.pvalue = np.full_like(value, np.nan)
                not_nan = ~np.isnan(value)
                self.pvalue[not_nan] = self.dist.sf(np.abs(value[not_nan])) * 2

        # cleanup
        # should we return python scalar?
        self.pvalue = np.squeeze(self.pvalue)