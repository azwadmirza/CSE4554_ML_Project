    def _run_convergence_checks(self, trace, model):
        if trace.nchains == 1:
            msg = ("Only one chain was sampled, this makes it impossible to "
                   "run some convergence checks")
            warn = SamplerWarning(WarningType.BAD_PARAMS, msg, 'info',
                                  None, None, None)
            self._add_warnings([warn])
            return

        from pymc3 import diagnostics

        valid_name = [rv.name for rv in model.free_RVs + model.deterministics]
        varnames = []
        for rv in model.free_RVs:
            rv_name = rv.name
            if is_transformed_name(rv_name):
                rv_name2 = get_untransformed_name(rv_name)
                rv_name = rv_name2 if rv_name2 in valid_name else rv_name
            if rv_name in trace.varnames:
                varnames.append(rv_name)

        self._effective_n = effective_n = diagnostics.effective_n(trace, varnames)
        self._gelman_rubin = gelman_rubin = diagnostics.gelman_rubin(trace, varnames)

        warnings = []
        rhat_max = max(val.max() for val in gelman_rubin.values())
        if rhat_max > 1.4:
            msg = ("The gelman-rubin statistic is larger than 1.4 for some "
                   "parameters. The sampler did not converge.")
            warn = SamplerWarning(
                WarningType.CONVERGENCE, msg, 'error', None, None, gelman_rubin)
            warnings.append(warn)
        elif rhat_max > 1.2:
            msg = ("The gelman-rubin statistic is larger than 1.2 for some "
                   "parameters.")
            warn = SamplerWarning(
                WarningType.CONVERGENCE, msg, 'warn', None, None, gelman_rubin)
            warnings.append(warn)
        elif rhat_max > 1.05:
            msg = ("The gelman-rubin statistic is larger than 1.05 for some "
                   "parameters. This indicates slight problems during "
                   "sampling.")
            warn = SamplerWarning(
                WarningType.CONVERGENCE, msg, 'info', None, None, gelman_rubin)
            warnings.append(warn)

        eff_min = min(val.min() for val in effective_n.values())
        n_samples = len(trace) * trace.nchains
        if eff_min < 200 and n_samples >= 500:
            msg = ("The estimated number of effective samples is smaller than "
                   "200 for some parameters.")
            warn = SamplerWarning(
                WarningType.CONVERGENCE, msg, 'error', None, None, effective_n)
            warnings.append(warn)
        elif eff_min / n_samples < 0.1:
            msg = ("The number of effective samples is smaller than "
                   "10% for some parameters.")
            warn = SamplerWarning(
                WarningType.CONVERGENCE, msg, 'warn', None, None, effective_n)
            warnings.append(warn)
        elif eff_min / n_samples < 0.25:
            msg = ("The number of effective samples is smaller than "
                   "25% for some parameters.")
            warn = SamplerWarning(
                WarningType.CONVERGENCE, msg, 'info', None, None, effective_n)
            warnings.append(warn)

        self._add_warnings(warnings)