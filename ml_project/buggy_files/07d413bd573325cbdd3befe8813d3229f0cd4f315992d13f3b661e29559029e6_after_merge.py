def init_nuts(init='auto', njobs=1, n_init=500000, model=None,
              random_seed=-1, progressbar=True, **kwargs):
    """Set up the mass matrix initialization for NUTS.

    NUTS convergence and sampling speed is extremely dependent on the
    choice of mass/scaling matrix. This function implements different
    methods for choosing or adapting the mass matrix.

    Parameters
    ----------
    init : str
        Initialization method to use.

        * auto : Choose a default initialization method automatically.
          Currently, this is `'advi+adapt_diag'`, but this can change in
          the future. If you depend on the exact behaviour, choose an
          initialization method explicitly.
        * adapt_diag : Start with a identity mass matrix and then adapt
          a diagonal based on the variance of the tuning samples.
        * advi+adapt_diag : Run ADVI and then adapt the resulting diagonal
          mass matrix based on the sample variance of the tuning samples.
        * advi+adapt_diag_grad : Run ADVI and then adapt the resulting
          diagonal mass matrix based on the variance of the gradients
          during tuning. This is **experimental** and might be removed
          in a future release.
        * advi : Run ADVI to estimate posterior mean and diagonal mass
          matrix.
        * advi_map: Initialize ADVI with MAP and use MAP as starting point.
        * map : Use the MAP as starting point. This is discouraged.
        * nuts : Run NUTS and estimate posterior mean and mass matrix from
          the trace.
    njobs : int
        Number of parallel jobs to start.
    n_init : int
        Number of iterations of initializer
        If 'ADVI', number of iterations, if 'nuts', number of draws.
    model : Model (optional if in `with` context)
    progressbar : bool
        Whether or not to display a progressbar for advi sampling.
    **kwargs : keyword arguments
        Extra keyword arguments are forwarded to pymc3.NUTS.

    Returns
    -------
    start : pymc3.model.Point
        Starting point for sampler
    nuts_sampler : pymc3.step_methods.NUTS
        Instantiated and initialized NUTS sampler object
    """
    model = pm.modelcontext(model)

    vars = kwargs.get('vars', model.vars)
    if set(vars) != set(model.vars):
        raise ValueError('Must use init_nuts on all variables of a model.')
    if not pm.model.all_continuous(vars):
        raise ValueError('init_nuts can only be used for models with only '
                         'continuous variables.')

    if not isinstance(init, str):
        raise TypeError('init must be a string.')

    if init is not None:
        init = init.lower()

    if init == 'auto':
        init = 'advi+adapt_diag'

    pm._log.info('Initializing NUTS using {}...'.format(init))

    random_seed = int(np.atleast_1d(random_seed)[0])

    cb = [
        pm.callbacks.CheckParametersConvergence(
            tolerance=1e-2, diff='absolute'),
        pm.callbacks.CheckParametersConvergence(
            tolerance=1e-2, diff='relative'),
    ]

    if init == 'adapt_diag':
        start = [model.test_point] * njobs
        mean = np.mean([model.dict_to_array(vals) for vals in start], axis=0)
        var = np.ones_like(mean)
        potential = quadpotential.QuadPotentialDiagAdapt(
            model.ndim, mean, var, 10)
        if njobs == 1:
            start = start[0]
    elif init == 'advi+adapt_diag_grad':
        approx = pm.fit(
            random_seed=random_seed,
            n=n_init, method='advi', model=model,
            callbacks=cb,
            progressbar=progressbar,
            obj_optimizer=pm.adagrad_window,
        )
        start = approx.sample(draws=njobs)
        start = list(start)
        stds = approx.gbij.rmap(approx.std.eval())
        cov = model.dict_to_array(stds) ** 2
        mean = approx.gbij.rmap(approx.mean.get_value())
        mean = model.dict_to_array(mean)
        weight = 50
        potential = quadpotential.QuadPotentialDiagAdaptGrad(
            model.ndim, mean, cov, weight)
        if njobs == 1:
            start = start[0]
    elif init == 'advi+adapt_diag':
        approx = pm.fit(
            random_seed=random_seed,
            n=n_init, method='advi', model=model,
            callbacks=cb,
            progressbar=progressbar,
            obj_optimizer=pm.adagrad_window,
        )
        start = approx.sample(draws=njobs)
        start = list(start)
        stds = approx.gbij.rmap(approx.std.eval())
        cov = model.dict_to_array(stds) ** 2
        mean = approx.gbij.rmap(approx.mean.get_value())
        mean = model.dict_to_array(mean)
        weight = 50
        potential = quadpotential.QuadPotentialDiagAdapt(
            model.ndim, mean, cov, weight)
        if njobs == 1:
            start = start[0]
    elif init == 'advi':
        approx = pm.fit(
            random_seed=random_seed,
            n=n_init, method='advi', model=model,
            callbacks=cb,
            progressbar=progressbar,
            obj_optimizer=pm.adagrad_window
        )  # type: pm.MeanField
        start = approx.sample(draws=njobs)
        start = list(start)
        stds = approx.gbij.rmap(approx.std.eval())
        cov = model.dict_to_array(stds) ** 2
        potential = quadpotential.QuadPotentialDiag(cov)
        if njobs == 1:
            start = start[0]
    elif init == 'advi_map':
        start = pm.find_MAP()
        approx = pm.MeanField(model=model, start=start)
        pm.fit(
            random_seed=random_seed,
            n=n_init, method=pm.ADVI.from_mean_field(approx),
            callbacks=cb,
            progressbar=progressbar,
            obj_optimizer=pm.adagrad_window
        )
        start = approx.sample(draws=njobs)
        start = list(start)
        stds = approx.gbij.rmap(approx.std.eval())
        cov = model.dict_to_array(stds) ** 2
        potential = quadpotential.QuadPotentialDiag(cov)
        if njobs == 1:
            start = start[0]
    elif init == 'map':
        start = pm.find_MAP()
        cov = pm.find_hessian(point=start)
        start = [start] * njobs
        potential = quadpotential.QuadPotentialFull(cov)
        if njobs == 1:
            start = start[0]
    elif init == 'nuts':
        init_trace = pm.sample(draws=n_init, step=pm.NUTS(),
                               tune=n_init // 2,
                               random_seed=random_seed)
        cov = np.atleast_1d(pm.trace_cov(init_trace))
        start = list(np.random.choice(init_trace, njobs))
        potential = quadpotential.QuadPotentialFull(cov)
        if njobs == 1:
            start = start[0]
    else:
        raise NotImplementedError('Initializer {} is not supported.'.format(init))

    step = pm.NUTS(potential=potential, **kwargs)

    return start, step