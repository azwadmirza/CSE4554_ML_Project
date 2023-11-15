    def fit(self, data):

        data_b0 = data[self.b0s_mask].mean()
        data_single_b0 = np.r_[data_b0, data[~self.b0s_mask]] / data_b0

        # calculates the mean signal at each b_values
        means = find_signal_means(self.b_unique,
                                  data_single_b0, 
                                  self.one_0_bvals,
                                  self.srm,
                                  self.lb_matrix_signal)

        # average diffusivity initialization
        x = np.array([np.pi/4, np.pi/4])

        x, status = leastsq(forecast_error_func, x,
                            args=(self.b_unique, means))

        # transform to bound the diffusivities from 0 to 3e-03
        d_par = np.cos(x[0])**2 * 3e-03
        d_perp = np.cos(x[1])**2 * 3e-03

        if d_perp >= d_par:
            temp = d_par
            d_par = d_perp
            d_perp = temp

        # round to avoid memory explosion
        diff_key = str(int(np.round(d_par * 1e05))) + \
            str(int(np.round(d_perp * 1e05)))

        M_diff = self.cache_get('forecast_matrix', key=diff_key)
        if M_diff is None:
            M_diff = forecast_matrix(
                self.sh_order,  d_par, d_perp, self.one_0_bvals)
            self.cache_set('forecast_matrix', key=diff_key, value=M_diff)

        M = M_diff * self.rho
        M0 = M[:, 0]
        c0 = np.sqrt(1.0/(4*np.pi))

        # coefficients vector initialization
        n_c = int((self.sh_order + 1)*(self.sh_order + 2)/2)
        coef = np.zeros(n_c)
        coef[0] = c0
        if int(np.round(d_par*1e05)) > int(np.round(d_perp*1e05)):
            if self.wls:
                data_r = data_single_b0 - M0*c0

                Mr = M[:, 1:]
                Lr = self.lb_matrix[1:, 1:]

                pseudo_inv = np.dot(np.linalg.inv(
                    np.dot(Mr.T, Mr) + self.lambda_lb*Lr), Mr.T)
                coef = np.dot(pseudo_inv, data_r)
                coef = np.r_[c0, coef]

            if self.csd:
                coef, _ = csdeconv(data_single_b0, M, self.fod, tau=0.1,
                                   convergence=50)
                coef = coef / coef[0] * c0

            if self.pos:
                c = cvxpy.Variable(M.shape[1])
                design_matrix = cvxpy.Constant(M)
                objective = cvxpy.Minimize(
                    cvxpy.sum_squares(design_matrix * c - data_single_b0) +
                    self.lambda_lb * cvxpy.quad_form(c, self.lb_matrix))

                constraints = [c[0] == c0, self.fod * c >= 0]
                prob = cvxpy.Problem(objective, constraints)
                try:
                    prob.solve(solver=cvxpy.OSQP, eps_abs=1e-05, eps_rel=1e-05)
                    coef = np.asarray(c.value).squeeze()
                except Exception:
                    warn('Optimization did not find a solution')
                    coef = np.zeros(M.shape[1])
                    coef[0] = c0

        return ForecastFit(self, data, coef, d_par, d_perp)