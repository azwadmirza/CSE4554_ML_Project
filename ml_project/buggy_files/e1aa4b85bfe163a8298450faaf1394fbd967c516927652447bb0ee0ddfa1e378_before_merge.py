    def _compute_reg_bw(self, bw):
        if not isinstance(bw, string_types):
            self._bw_method = "user-specified"
            return np.asarray(bw)
        else:
            # The user specified a bandwidth selection method e.g. 'cv_ls'
            self._bw_method = bw
            res = self.bw_func[bw]
            X = np.std(self.exog, axis=0)
            h0 = 1.06 * X * \
                 self.nobs ** (- 1. / (4 + np.size(self.exog, axis=1)))

            func = self.est[self.reg_type]
            bw_estimated = optimize.fmin(res, x0=h0, args=(func, ),
                                         maxiter=1e3, maxfun=1e3, disp=0)
            return bw_estimated