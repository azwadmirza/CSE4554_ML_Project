    def initialize(self):
        if not self.score:  # right now score is not optional
            self.score = approx_fprime
            if not self.hessian:
                pass
        else:   # can use approx_hess_p if we have a gradient
            if not self.hessian:
                pass
        #Initialize is called by
        #statsmodels.model.LikelihoodModel.__init__
        #and should contain any preprocessing that needs to be done for a model
        from statsmodels.tools import tools
        if self.exog is not None:
            # assume constant
            er = np_matrix_rank(self.exog)
            self.df_model = float(er - 1)
            self.df_resid = float(self.exog.shape[0] - er)
        else:
            self.df_model = np.nan
            self.df_resid = np.nan
        super(GenericLikelihoodModel, self).initialize()