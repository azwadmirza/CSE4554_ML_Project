    def fit(self, fitter=None, method='ls', grad=False,
            bounded=False, ext_bounding=False, update_plot=False,
            **kwargs):
        """Fits the model to the experimental data.

        The chi-squared, reduced chi-squared and the degrees of freedom are
        computed automatically when fitting. They are stored as signals, in the
        `chisq`, `red_chisq`  and `dof`. Note that,
        unless ``metadata.Signal.Noise_properties.variance`` contains an
        accurate estimation of the variance of the data, the chi-squared and
        reduced chi-squared cannot be computed correctly. This is also true for
        homocedastic noise.

        Parameters
        ----------
        fitter : {None, "leastsq", "odr", "mpfit", "fmin"}
            The optimizer to perform the fitting. If None the fitter
            defined in `preferences.Model.default_fitter` is used.
            "leastsq" performs least squares using the Levenberg–Marquardt
            algorithm.
            "mpfit"  performs least squares using the Levenberg–Marquardt
            algorithm and, unlike "leastsq", support bounded optimization.
            "fmin" performs curve fitting using a downhill simplex algorithm.
            It is less robust than the Levenberg-Marquardt based optimizers,
            but, at present, it is the only one that support maximum likelihood
            optimization for poissonian noise.
            "odr" performs the optimization using the orthogonal distance
            regression algorithm. It does not support bounds.
            "leastsq", "odr" and "mpfit" can estimate the standard deviation of
            the estimated value of the parameters if the
            "metada.Signal.Noise_properties.variance" attribute is defined.
            Note that if it is not defined the standard deviation is estimated
            using variance equal 1, what, if the noise is heterocedatic, will
            result in a biased estimation of the parameter values and errors.i
            If `variance` is a `Signal` instance of the
            same `navigation_dimension` as the spectrum, and `method` is "ls"
            weighted least squares is performed.
        method : {'ls', 'ml'}
            Choose 'ls' (default) for least squares and 'ml' for poissonian
            maximum-likelihood estimation.  The latter is only available when
            `fitter` is "fmin".
        grad : bool
            If True, the analytical gradient is used if defined to
            speed up the optimization.
        bounded : bool
            If True performs bounded optimization if the fitter
            supports it. Currently only "mpfit" support it.
        update_plot : bool
            If True, the plot is updated during the optimization
            process. It slows down the optimization but it permits
            to visualize the optimization progress.
        ext_bounding : bool
            If True, enforce bounding by keeping the value of the
            parameters constant out of the defined bounding area.

        **kwargs : key word arguments
            Any extra key word argument will be passed to the chosen
            fitter. For more information read the docstring of the optimizer
            of your choice in `scipy.optimize`.

        See Also
        --------
        multifit

        """

        if fitter is None:
            fitter = preferences.Model.default_fitter
        switch_aap = (update_plot != self._plot_active)
        if switch_aap is True and update_plot is False:
            self._disconnect_parameters2update_plot()

        self.p_std = None
        self._set_p0()
        if ext_bounding:
            self._enable_ext_bounding()
        if grad is False:
            approx_grad = True
            jacobian = None
            odr_jacobian = None
            grad_ml = None
            grad_ls = None
        else:
            approx_grad = False
            jacobian = self._jacobian
            odr_jacobian = self._jacobian4odr
            grad_ml = self._gradient_ml
            grad_ls = self._gradient_ls

        if bounded is True and fitter not in ("mpfit", "tnc", "l_bfgs_b"):
            raise NotImplementedError("Bounded optimization is only available "
                                      "for the mpfit optimizer.")
        if method == 'ml':
            weights = None
            if fitter != "fmin":
                raise NotImplementedError("Maximum likelihood estimation "
                                          'is only implemented for the "fmin" '
                                          'optimizer')
        elif method == "ls":
            if ("Signal.Noise_properties.variance" not in
                    self.spectrum.metadata):
                variance = 1
            else:
                variance = self.spectrum.metadata.Signal.\
                    Noise_properties.variance
                if isinstance(variance, Signal):
                    if (variance.axes_manager.navigation_shape ==
                            self.spectrum.axes_manager.navigation_shape):
                        variance = variance.data.__getitem__(
                            self.axes_manager._getitem_tuple)[
                            self.channel_switches]
                    else:
                        raise AttributeError(
                            "The `navigation_shape` of the variance signals "
                            "is not equal to the variance shape of the "
                            "spectrum")
                elif not isinstance(variance, numbers.Number):
                    raise AttributeError(
                        "Variance must be a number or a `Signal` instance but "
                        "currently it is a %s" % type(variance))

            weights = 1. / np.sqrt(variance)
        else:
            raise ValueError(
                'method must be "ls" or "ml" but %s given' %
                method)
        args = (self.spectrum()[self.channel_switches],
                weights)

        # Least squares "dedicated" fitters
        if fitter == "leastsq":
            output = \
                leastsq(self._errfunc, self.p0[:], Dfun=jacobian,
                        col_deriv=1, args=args, full_output=True, **kwargs)

            self.p0, pcov = output[0:2]

            if (self.axis.size > len(self.p0)) and pcov is not None:
                pcov *= ((self._errfunc(self.p0, *args) ** 2).sum() /
                         (len(args[0]) - len(self.p0)))
                self.p_std = np.sqrt(np.diag(pcov))
            self.fit_output = output

        elif fitter == "odr":
            modelo = odr.Model(fcn=self._function4odr,
                               fjacb=odr_jacobian)
            mydata = odr.RealData(
                self.axis.axis[
                    self.channel_switches], self.spectrum()[
                    self.channel_switches], sx=None, sy=(
                    1 / weights if weights is not None else None))
            myodr = odr.ODR(mydata, modelo, beta0=self.p0[:])
            myoutput = myodr.run()
            result = myoutput.beta
            self.p_std = myoutput.sd_beta
            self.p0 = result
            self.fit_output = myoutput

        elif fitter == 'mpfit':
            autoderivative = 1
            if grad is True:
                autoderivative = 0
            if bounded is True:
                self.set_mpfit_parameters_info()
            elif bounded is False:
                self.mpfit_parinfo = None
            m = mpfit(self._errfunc4mpfit, self.p0[:],
                      parinfo=self.mpfit_parinfo, functkw={
                          'y': self.spectrum()[self.channel_switches],
                          'weights': weights}, autoderivative=autoderivative,
                      quiet=1)
            self.p0 = m.params
            if (self.axis.size > len(self.p0)) and m.perror is not None:
                self.p_std = m.perror * np.sqrt(
                    (self._errfunc(self.p0, *args) ** 2).sum() /
                    (len(args[0]) - len(self.p0)))
            self.fit_output = m
        else:
            # General optimizers (incluiding constrained ones(tnc,l_bfgs_b)
            # Least squares or maximum likelihood
            if method == 'ml':
                tominimize = self._poisson_likelihood_function
                fprime = grad_ml
            elif method in ['ls', "wls"]:
                tominimize = self._errfunc2
                fprime = grad_ls

            # OPTIMIZERS

            # Simple (don't use gradient)
            if fitter == "fmin":
                self.p0 = fmin(
                    tominimize, self.p0, args=args, **kwargs)
            elif fitter == "powell":
                self.p0 = fmin_powell(tominimize, self.p0, args=args,
                                      **kwargs)

            # Make use of the gradient
            elif fitter == "cg":
                self.p0 = fmin_cg(tominimize, self.p0, fprime=fprime,
                                  args=args, **kwargs)
            elif fitter == "ncg":
                self.p0 = fmin_ncg(tominimize, self.p0, fprime=fprime,
                                   args=args, **kwargs)
            elif fitter == "bfgs":
                self.p0 = fmin_bfgs(
                    tominimize, self.p0, fprime=fprime,
                    args=args, **kwargs)

            # Constrainded optimizers

            # Use gradient
            elif fitter == "tnc":
                if bounded is True:
                    self.set_boundaries()
                elif bounded is False:
                    self.self.free_parameters_boundaries = None
                self.p0 = fmin_tnc(
                    tominimize,
                    self.p0,
                    fprime=fprime,
                    args=args,
                    bounds=self.free_parameters_boundaries,
                    approx_grad=approx_grad,
                    **kwargs)[0]
            elif fitter == "l_bfgs_b":
                if bounded is True:
                    self.set_boundaries()
                elif bounded is False:
                    self.self.free_parameters_boundaries = None
                self.p0 = fmin_l_bfgs_b(tominimize, self.p0,
                                        fprime=fprime, args=args,
                                        bounds=self.free_parameters_boundaries,
                                        approx_grad=approx_grad, **kwargs)[0]
            else:
                print("""
                The %s optimizer is not available.

                Available optimizers:
                Unconstrained:
                --------------
                Only least Squares: leastsq and odr
                General: fmin, powell, cg, ncg, bfgs

                Cosntrained:
                ------------
                tnc and l_bfgs_b
                """ % fitter)
        if np.iterable(self.p0) == 0:
            self.p0 = (self.p0,)
        self._fetch_values_from_p0(p_std=self.p_std)
        self.store_current_values()
        self._calculate_chisq()
        self._set_current_degrees_of_freedom()
        if ext_bounding is True:
            self._disable_ext_bounding()
        if switch_aap is True and update_plot is False:
            self._connect_parameters2update_plot()
            self.update_plot()