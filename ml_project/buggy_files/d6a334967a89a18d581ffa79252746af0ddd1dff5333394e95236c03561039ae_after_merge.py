def analyze(problem, X, Y,
            num_resamples=100,
            conf_level=0.95,
            print_to_console=False,
            num_levels=4,
            seed=None):
    """Perform Morris Analysis on model outputs.

    Returns a dictionary with keys 'mu', 'mu_star', 'sigma', and
    'mu_star_conf', where each entry is a list of parameters containing
    the indices in the same order as the parameter file.

    Arguments
    ---------
    problem : dict
        The problem definition
    X : numpy.matrix
        The NumPy matrix containing the model inputs of dtype=float
    Y : numpy.array
        The NumPy array containing the model outputs of dtype=float
    num_resamples : int
        The number of resamples used to compute the confidence
        intervals (default 1000)
    conf_level : float
        The confidence interval level (default 0.95)
    print_to_console : bool
        Print results directly to console (default False)
    num_levels : int
        The number of grid levels, must be identical to the value
        passed to SALib.sample.morris (default 4)

    Returns
    -------
    Si : dict
        A dictionary of sensitivity indices containing the following entries.

        - `mu` - the mean elementary effect
        - `mu_star` - the absolute of the mean elementary effect
        - `sigma` - the standard deviation of the elementary effect
        - `mu_star_conf` - the bootstrapped confidence interval
        - `names` - the names of the parameters

    References
    ----------
    .. [1] Morris, M. (1991).  "Factorial Sampling Plans for Preliminary
           Computational Experiments."  Technometrics, 33(2):161-174,
           doi:10.1080/00401706.1991.10484804.
    .. [2] Campolongo, F., J. Cariboni, and A. Saltelli (2007).  "An effective
           screening design for sensitivity analysis of large models."
           Environmental Modelling & Software, 22(10):1509-1518,
           doi:10.1016/j.envsoft.2006.10.004.

    Examples
    --------
    >>> X = morris.sample(problem, 1000, num_levels=4)
    >>> Y = Ishigami.evaluate(X)
    >>> Si = morris.analyze(problem, X, Y, conf_level=0.95,
    >>>                     print_to_console=True, num_levels=4)

    """
    if seed:
        np.random.seed(seed)

    msg = ("dtype of {} array must be 'float', float32 or float64")
    if X.dtype not in ['float', 'float32', 'float64']:
        raise ValueError(msg.format('X'))
    if Y.dtype not in ['float', 'float32', 'float64']:
        raise ValueError(msg.format('Y'))

    # Assume that there are no groups
    groups = None
    delta = _compute_delta(num_levels)

    num_vars = problem['num_vars']

    if (problem.get('groups') is None) & (Y.size % (num_vars + 1) == 0):
        num_trajectories = int(Y.size / (num_vars + 1))
    elif problem.get('groups') is not None:
        groups, unique_group_names = compute_groups_matrix(
            problem['groups'])
        number_of_groups = len(unique_group_names)
        num_trajectories = int(Y.size / (number_of_groups + 1))
    else:
        raise ValueError("Number of samples in model output file must be"
                         "a multiple of (D+1), where D is the number of"
                         "parameters (or groups) in your parameter file.")
    ee = np.zeros((num_vars, num_trajectories))
    ee = compute_elementary_effects(
        X, Y, int(Y.size / num_trajectories), delta)

    # Output the Mu, Mu*, and Sigma Values. Also return them in case this is
    # being called from Python
    Si = ResultDict((k, [None] * num_vars)
                    for k in ['names', 'mu', 'mu_star', 'sigma', 'mu_star_conf'])
    Si['mu'] = np.average(ee, 1)
    Si['mu_star'] = np.average(np.abs(ee), 1)
    Si['sigma'] = np.std(ee, axis=1, ddof=1)
    Si['names'] = problem['names']

    for j in range(num_vars):
        Si['mu_star_conf'][j] = compute_mu_star_confidence(
            ee[j, :], num_trajectories, num_resamples, conf_level)

    if groups is None:
        if print_to_console:
            print("{0:<30} {1:>10} {2:>10} {3:>15} {4:>10}".format(
                "Parameter",
                "Mu_Star",
                "Mu",
                "Mu_Star_Conf",
                "Sigma")
            )
            for j in list(range(num_vars)):
                print("{0:30} {1:10.3f} {2:10.3f} {3:15.3f} {4:10.3f}".format(
                    Si['names'][j],
                    Si['mu_star'][j],
                    Si['mu'][j],
                    Si['mu_star_conf'][j],
                    Si['sigma'][j])
                )
        return Si
    elif groups is not None:
        # if there are groups, then the elementary effects returned need to be
        # computed over the groups of variables,
        # rather than the individual variables
        Si_grouped = ResultDict((k, [None] * num_vars)
                                for k in ['mu_star', 'mu_star_conf'])
        Si_grouped['mu_star'] = compute_grouped_metric(Si['mu_star'], groups)
        Si_grouped['mu_star_conf'] = compute_grouped_metric(Si['mu_star_conf'],
                                                            groups)
        Si_grouped['names'] = unique_group_names
        Si_grouped['sigma'] = compute_grouped_sigma(Si['sigma'], groups)
        Si_grouped['mu'] = compute_grouped_sigma(Si['mu'], groups)

        if print_to_console:
            print("{0:<30} {1:>10} {2:>10} {3:>15} {4:>10}".format(
                "Parameter",
                "Mu_Star",
                "Mu",
                "Mu_Star_Conf",
                "Sigma")
            )
            for j in list(range(number_of_groups)):
                print("{0:30} {1:10.3f} {2:10.3f} {3:15.3f} {4:10.3f}".format(
                    Si_grouped['names'][j],
                    Si_grouped['mu_star'][j],
                    Si_grouped['mu'][j],
                    Si_grouped['mu_star_conf'][j],
                    Si_grouped['sigma'][j])
                )

        return Si_grouped
    else:
        raise RuntimeError(
            "Could not determine which parameters should be returned")