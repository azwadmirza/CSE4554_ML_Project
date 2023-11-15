def sample(
    draws=1000,
    step=None,
    init="auto",
    n_init=200000,
    start=None,
    trace=None,
    chain_idx=0,
    chains=None,
    cores=None,
    tune=1000,
    progressbar=True,
    model=None,
    random_seed=None,
    discard_tuned_samples=True,
    compute_convergence_checks=True,
    callback=None,
    *,
    return_inferencedata=None,
    idata_kwargs: dict = None,
    mp_ctx=None,
    pickle_backend: str = "pickle",
    **kwargs,
):
    """Draw samples from the posterior using the given step methods.

    Multiple step methods are supported via compound step methods.

    Parameters
    ----------
    draws : int
        The number of samples to draw. Defaults to 1000. The number of tuned samples are discarded
        by default. See ``discard_tuned_samples``.
    init : str
        Initialization method to use for auto-assigned NUTS samplers.

        * auto: Choose a default initialization method automatically.
          Currently, this is ``jitter+adapt_diag``, but this can change in the future.
          If you depend on the exact behaviour, choose an initialization method explicitly.
        * adapt_diag: Start with a identity mass matrix and then adapt a diagonal based on the
          variance of the tuning samples. All chains use the test value (usually the prior mean)
          as starting point.
        * jitter+adapt_diag: Same as ``adapt_diag``, but add uniform jitter in [-1, 1] to the
          starting point in each chain.
        * advi+adapt_diag: Run ADVI and then adapt the resulting diagonal mass matrix based on the
          sample variance of the tuning samples.
        * advi+adapt_diag_grad: Run ADVI and then adapt the resulting diagonal mass matrix based
          on the variance of the gradients during tuning. This is **experimental** and might be
          removed in a future release.
        * advi: Run ADVI to estimate posterior mean and diagonal mass matrix.
        * advi_map: Initialize ADVI with MAP and use MAP as starting point.
        * map: Use the MAP as starting point. This is discouraged.
        * adapt_full: Adapt a dense mass matrix using the sample covariances

    step : function or iterable of functions
        A step function or collection of functions. If there are variables without step methods,
        step methods for those variables will be assigned automatically.  By default the NUTS step
        method will be used, if appropriate to the model; this is a good default for beginning
        users.
    n_init : int
        Number of iterations of initializer. Only works for 'ADVI' init methods.
    start : dict, or array of dict
        Starting point in parameter space (or partial point)
        Defaults to ``trace.point(-1))`` if there is a trace provided and model.test_point if not
        (defaults to empty dict). Initialization methods for NUTS (see ``init`` keyword) can
        overwrite the default.
    trace : backend, list, or MultiTrace
        This should be a backend instance, a list of variables to track, or a MultiTrace object
        with past values. If a MultiTrace object is given, it must contain samples for the chain
        number ``chain``. If None or a list of variables, the NDArray backend is used.
    chain_idx : int
        Chain number used to store sample in backend. If ``chains`` is greater than one, chain
        numbers will start here.
    chains : int
        The number of chains to sample. Running independent chains is important for some
        convergence statistics and can also reveal multiple modes in the posterior. If ``None``,
        then set to either ``cores`` or 2, whichever is larger.
    cores : int
        The number of chains to run in parallel. If ``None``, set to the number of CPUs in the
        system, but at most 4.
    tune : int
        Number of iterations to tune, defaults to 1000. Samplers adjust the step sizes, scalings or
        similar during tuning. Tuning samples will be drawn in addition to the number specified in
        the ``draws`` argument, and will be discarded unless ``discard_tuned_samples`` is set to
        False.
    progressbar : bool, optional default=True
        Whether or not to display a progress bar in the command line. The bar shows the percentage
        of completion, the sampling speed in samples per second (SPS), and the estimated remaining
        time until completion ("expected time of arrival"; ETA).
    model : Model (optional if in ``with`` context)
    random_seed : int or list of ints
        A list is accepted if ``cores`` is greater than one.
    discard_tuned_samples : bool
        Whether to discard posterior samples of the tune interval.
    compute_convergence_checks : bool, default=True
        Whether to compute sampler statistics like Gelman-Rubin and ``effective_n``.
    callback : function, default=None
        A function which gets called for every sample from the trace of a chain. The function is
        called with the trace and the current draw and will contain all samples for a single trace.
        the ``draw.chain`` argument can be used to determine which of the active chains the sample
        is drawn from.

        Sampling can be interrupted by throwing a ``KeyboardInterrupt`` in the callback.
    return_inferencedata : bool, default=False
        Whether to return the trace as an :class:`arviz:arviz.InferenceData` (True) object or a `MultiTrace` (False)
        Defaults to `False`, but we'll switch to `True` in an upcoming release.
    idata_kwargs : dict, optional
        Keyword arguments for :func:`arviz:arviz.from_pymc3`
    mp_ctx : multiprocessing.context.BaseContent
        A multiprocessing context for parallel sampling. See multiprocessing
        documentation for details.
    pickle_backend : str
        One of `'pickle'` or `'dill'`. The library used to pickle models
        in parallel sampling if the multiprocessing context is not of type
        `fork`.

    Returns
    -------
    trace : pymc3.backends.base.MultiTrace or arviz.InferenceData
        A ``MultiTrace`` or ArviZ ``InferenceData`` object that contains the samples.

    Notes
    -----
    Optional keyword arguments can be passed to ``sample`` to be delivered to the
    ``step_method``s used during sampling.

    If your model uses only one step method, you can address step method kwargs
    directly. In particular, the NUTS step method has several options including:

        * target_accept : float in [0, 1]. The step size is tuned such that we
          approximate this acceptance rate. Higher values like 0.9 or 0.95 often
          work better for problematic posteriors
        * max_treedepth : The maximum depth of the trajectory tree
        * step_scale : float, default 0.25
          The initial guess for the step size scaled down by :math:`1/n**(1/4)`

    If your model uses multiple step methods, aka a Compound Step, then you have
    two ways to address arguments to each step method:

        A: If you let ``sample()`` automatically assign the ``step_method``s,
         and you can correctly anticipate what they will be, then you can wrap
         step method kwargs in a dict and pass that to sample() with a kwarg set
         to the name of the step method.
         e.g. for a CompoundStep comprising NUTS and BinaryGibbsMetropolis,
         you could send:
            1. ``target_accept`` to NUTS: nuts={'target_accept':0.9}
            2. ``transit_p`` to BinaryGibbsMetropolis: binary_gibbs_metropolis={'transit_p':.7}

         Note that available names are:
            ``nuts``, ``hmc``, ``metropolis``, ``binary_metropolis``,
            ``binary_gibbs_metropolis``, ``categorical_gibbs_metropolis``,
            ``DEMetropolis``, ``DEMetropolisZ``, ``slice``

        B: If you manually declare the ``step_method``s, within the ``step``
         kwarg, then you can address the ``step_method`` kwargs directly.
         e.g. for a CompoundStep comprising NUTS and BinaryGibbsMetropolis,
         you could send:
            step=[pm.NUTS([freeRV1, freeRV2], target_accept=0.9),
                  pm.BinaryGibbsMetropolis([freeRV3], transit_p=.7)]

    You can find a full list of arguments in the docstring of the step methods.

    Examples
    --------
    .. code:: ipython

        >>> import pymc3 as pm
        ... n = 100
        ... h = 61
        ... alpha = 2
        ... beta = 2

    .. code:: ipython

        >>> with pm.Model() as model: # context management
        ...     p = pm.Beta('p', alpha=alpha, beta=beta)
        ...     y = pm.Binomial('y', n=n, p=p, observed=h)
        ...     trace = pm.sample()
        >>> pm.summary(trace)
               mean        sd  mc_error   hpd_2.5  hpd_97.5
        p  0.604625  0.047086   0.00078  0.510498  0.694774

    """
    model = modelcontext(model)
    if start is None:
        start = model.test_point
    else:
        if isinstance(start, dict):
            update_start_vals(start, model.test_point, model)
        else:
            for chain_start_vals in start:
                update_start_vals(chain_start_vals, model.test_point, model)

    check_start_vals(start, model)
    if cores is None:
        cores = min(4, _cpu_count())

    if chains is None:
        chains = max(2, cores)
    if isinstance(start, dict):
        start = [start] * chains
    if random_seed == -1:
        random_seed = None
    if chains == 1 and isinstance(random_seed, int):
        random_seed = [random_seed]
    if random_seed is None or isinstance(random_seed, int):
        if random_seed is not None:
            np.random.seed(random_seed)
        random_seed = [np.random.randint(2 ** 30) for _ in range(chains)]
    if not isinstance(random_seed, Iterable):
        raise TypeError("Invalid value for `random_seed`. Must be tuple, list or int")

    if not discard_tuned_samples and not return_inferencedata:
        warnings.warn(
            "Tuning samples will be included in the returned `MultiTrace` object, which can lead to"
            " complications in your downstream analysis. Please consider to switch to `InferenceData`:\n"
            "`pm.sample(..., return_inferencedata=True)`",
            UserWarning,
        )

    if return_inferencedata is None:
        v = packaging.version.parse(pm.__version__)
        if v.release[0] > 3 or v.release[1] >= 10:  # type: ignore
            warnings.warn(
                "In an upcoming release, pm.sample will return an `arviz.InferenceData` object instead of a `MultiTrace` by default. "
                "You can pass return_inferencedata=True or return_inferencedata=False to be safe and silence this warning.",
                FutureWarning,
            )
        # set the default
        return_inferencedata = False

    if start is not None:
        for start_vals in start:
            _check_start_shape(model, start_vals)

    # small trace warning
    if draws == 0:
        msg = "Tuning was enabled throughout the whole trace."
        _log.warning(msg)
    elif draws < 500:
        msg = "Only %s samples in chain." % draws
        _log.warning(msg)

    draws += tune

    if model.ndim == 0:
        raise ValueError("The model does not contain any free variables.")

    if step is None and init is not None and all_continuous(model.vars):
        try:
            # By default, try to use NUTS
            _log.info("Auto-assigning NUTS sampler...")
            start_, step = init_nuts(
                init=init,
                chains=chains,
                n_init=n_init,
                model=model,
                random_seed=random_seed,
                progressbar=progressbar,
                **kwargs,
            )
            check_start_vals(start_, model)
            if start is None:
                start = start_
        except (AttributeError, NotImplementedError, tg.NullTypeGradError):
            # gradient computation failed
            _log.info("Initializing NUTS failed. " "Falling back to elementwise auto-assignment.")
            _log.debug("Exception in init nuts", exec_info=True)
            step = assign_step_methods(model, step, step_kwargs=kwargs)
    else:
        step = assign_step_methods(model, step, step_kwargs=kwargs)

    if isinstance(step, list):
        step = CompoundStep(step)
    if start is None:
        start = {}
    if isinstance(start, dict):
        start = [start] * chains

    sample_args = {
        "draws": draws,
        "step": step,
        "start": start,
        "trace": trace,
        "chain": chain_idx,
        "chains": chains,
        "tune": tune,
        "progressbar": progressbar,
        "model": model,
        "random_seed": random_seed,
        "cores": cores,
        "callback": callback,
        "discard_tuned_samples": discard_tuned_samples,
    }
    parallel_args = {
        "pickle_backend": pickle_backend,
        "mp_ctx": mp_ctx,
    }

    sample_args.update(kwargs)

    has_population_samplers = np.any(
        [
            isinstance(m, arraystep.PopulationArrayStepShared)
            for m in (step.methods if isinstance(step, CompoundStep) else [step])
        ]
    )

    parallel = cores > 1 and chains > 1 and not has_population_samplers
    t_start = time.time()
    if parallel:
        _log.info(f"Multiprocess sampling ({chains} chains in {cores} jobs)")
        _print_step_hierarchy(step)
        try:
            trace = _mp_sample(**sample_args, **parallel_args)
        except pickle.PickleError:
            _log.warning("Could not pickle model, sampling singlethreaded.")
            _log.debug("Pickling error:", exec_info=True)
            parallel = False
        except AttributeError as e:
            if str(e).startswith("AttributeError: Can't pickle"):
                _log.warning("Could not pickle model, sampling singlethreaded.")
                _log.debug("Pickling error:", exec_info=True)
                parallel = False
            else:
                raise
    if not parallel:
        if has_population_samplers:
            has_demcmc = np.any(
                [
                    isinstance(m, DEMetropolis)
                    for m in (step.methods if isinstance(step, CompoundStep) else [step])
                ]
            )
            _log.info(f"Population sampling ({chains} chains)")
            if has_demcmc and chains < 3:
                raise ValueError(
                    "DEMetropolis requires at least 3 chains. "
                    "For this {}-dimensional model you should use ≥{} chains".format(
                        model.ndim, model.ndim + 1
                    )
                )
            if has_demcmc and chains <= model.ndim:
                warnings.warn(
                    "DEMetropolis should be used with more chains than dimensions! "
                    "(The model has {} dimensions.)".format(model.ndim),
                    UserWarning,
                )
            _print_step_hierarchy(step)
            trace = _sample_population(parallelize=cores > 1, **sample_args)
        else:
            _log.info(f"Sequential sampling ({chains} chains in 1 job)")
            _print_step_hierarchy(step)
            trace = _sample_many(**sample_args)

    t_sampling = time.time() - t_start
    # count the number of tune/draw iterations that happened
    # ideally via the "tune" statistic, but not all samplers record it!
    if "tune" in trace.stat_names:
        stat = trace.get_sampler_stats("tune", chains=0)
        # when CompoundStep is used, the stat is 2 dimensional!
        if len(stat.shape) == 2:
            stat = stat[:, 0]
        stat = tuple(stat)
        n_tune = stat.count(True)
        n_draws = stat.count(False)
    else:
        # these may be wrong when KeyboardInterrupt happened, but they're better than nothing
        n_tune = min(tune, len(trace))
        n_draws = max(0, len(trace) - n_tune)

    if discard_tuned_samples:
        trace = trace[n_tune:]

    # save metadata in SamplerReport
    trace.report._n_tune = n_tune
    trace.report._n_draws = n_draws
    trace.report._t_sampling = t_sampling

    if "variable_inclusion" in trace.stat_names:
        variable_inclusion = np.stack(trace.get_sampler_stats("variable_inclusion")).mean(0)
        trace.report.variable_importance = variable_inclusion / variable_inclusion.sum()

    n_chains = len(trace.chains)
    _log.info(
        f'Sampling {n_chains} chain{"s" if n_chains > 1 else ""} for {n_tune:_d} tune and {n_draws:_d} draw iterations '
        f"({n_tune*n_chains:_d} + {n_draws*n_chains:_d} draws total) "
        f"took {trace.report.t_sampling:.0f} seconds."
    )

    idata = None
    if compute_convergence_checks or return_inferencedata:
        ikwargs = dict(model=model, save_warmup=not discard_tuned_samples)
        if idata_kwargs:
            ikwargs.update(idata_kwargs)
        idata = arviz.from_pymc3(trace, **ikwargs)

    if compute_convergence_checks:
        if draws - tune < 100:
            warnings.warn("The number of samples is too small to check convergence reliably.")
        else:
            trace.report._run_convergence_checks(idata, model)
    trace.report._log_summary()

    if return_inferencedata:
        return idata
    else:
        return trace