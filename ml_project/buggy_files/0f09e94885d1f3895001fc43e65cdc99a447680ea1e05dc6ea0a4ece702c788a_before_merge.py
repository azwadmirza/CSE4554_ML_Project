def analyze(problem, X, Y, num_resamples=10,
            conf_level=0.95, print_to_console=False, seed=None):
    """Perform Delta Moment-Independent Analysis on model outputs.

    Returns a dictionary with keys 'delta', 'delta_conf', 'S1', and 'S1_conf',
    where each entry is a list of size D (the number of parameters) containing
    the indices in the same order as the parameter file.

    Parameters
    ----------
    problem : dict
        The problem definition
    X: numpy.matrix
        A NumPy matrix containing the model inputs
    Y : numpy.array
        A NumPy array containing the model outputs
    num_resamples : int
        The number of resamples when computing confidence intervals (default 10)
    conf_level : float
        The confidence interval level (default 0.95)
    print_to_console : bool
        Print results directly to console (default False)

    References
    ----------
    .. [1] Borgonovo, E. (2007). "A new uncertainty importance measure."
           Reliability Engineering & System Safety, 92(6):771-784,
           doi:10.1016/j.ress.2006.04.015.

    .. [2] Plischke, E., E. Borgonovo, and C. L. Smith (2013). "Global
           sensitivity measures from given data." European Journal of
           Operational Research, 226(3):536-550, doi:10.1016/j.ejor.2012.11.047.

    Examples
    --------
    >>> X = latin.sample(problem, 1000)
    >>> Y = Ishigami.evaluate(X)
    >>> Si = delta.analyze(problem, X, Y, print_to_console=True)
    """
    if seed:
        np.random.seed(seed)

    D = problem['num_vars']
    N = Y.size

    if not 0 < conf_level < 1:
        raise RuntimeError("Confidence level must be between 0-1.")

    # equal frequency partition
    exp = (2 / (7 + np.tanh((1500 - N) / 500)))
    M = int(np.round( min(int(np.ceil(N**exp)), 48) ))
    m = np.linspace(0, N, M + 1)
    Ygrid = np.linspace(np.min(Y), np.max(Y), 100)

    keys = ('delta', 'delta_conf', 'S1', 'S1_conf')
    S = ResultDict((k, np.zeros(D)) for k in keys)
    S['names'] = problem['names']

    if print_to_console:
        print("Parameter %s %s %s %s" % keys)

    try:
        for i in range(D):
            X_i = X[:, i]
            S['delta'][i], S['delta_conf'][i] = bias_reduced_delta(
                Y, Ygrid, X_i, m, num_resamples, conf_level)
            S['S1'][i] = sobol_first(Y, X_i, m)
            S['S1_conf'][i] = sobol_first_conf(
                Y, X_i, m, num_resamples, conf_level)
            if print_to_console:
                print("%s %f %f %f %f" % (S['names'][i], S['delta'][
                    i], S['delta_conf'][i], S['S1'][i], S['S1_conf'][i]))
    except np.linalg.LinAlgError as e:
        msg = "Singular matrix detected\n"
        msg += "This may be due to the sample size ({}) being too small\n".format(Y.size)
        msg += "If this is not the case, check Y values or raise an issue with the\n"
        msg += "SALib team"

        raise np.linalg.LinAlgError(msg)

    return S