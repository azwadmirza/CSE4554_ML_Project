    def predict(self, params, exog=None, exposure=None, offset=None,
                linear=False):
        """
        Predict response variable of a count model given exogenous variables.

        Notes
        -----
        If exposure is specified, then it will be logged by the method.
        The user does not need to log it first.
        """
        #TODO: add offset tp
        if exog is None:
            exog = self.exog
            offset = getattr(self, 'offset', 0)
            exposure = getattr(self, 'exposure', 0)

        else:
            if exposure is None:
                exposure = 0
            else:
                exposure = np.log(exposure)
            if offset is None:
                offset = 0

        if not linear:
            return np.exp(np.dot(exog, params) + exposure + offset) # not cdf
        else:
            return np.dot(exog, params) + exposure + offset
            return super(CountModel, self).predict(params, exog, linear)