def lasso_stability_path(X, y, scaling=0.5, random_state=None,
                         n_resampling=200, n_grid=100,
                         sample_fraction=0.75,
                         eps=4 * np.finfo(np.float).eps, n_jobs=None,
                         verbose=False):
    """Stability path based on randomized Lasso estimates

    Parameters
    ----------
    X : array-like, shape = [n_samples, n_features]
        training data.

    y : array-like, shape = [n_samples]
        target values.

    scaling : float, optional, default=0.5
        The alpha parameter in the stability selection article used to
        randomly scale the features. Should be between 0 and 1.

    random_state : int, RandomState instance or None, optional, default=None
        The generator used to randomize the design.  If int, random_state is
        the seed used by the random number generator; If RandomState instance,
        random_state is the random number generator; If None, the random number
        generator is the RandomState instance used by `np.random`.

    n_resampling : int, optional, default=200
        Number of randomized models.

    n_grid : int, optional, default=100
        Number of grid points. The path is linearly reinterpolated
        on a grid between 0 and 1 before computing the scores.

    sample_fraction : float, optional, default=0.75
        The fraction of samples to be used in each randomized design.
        Should be between 0 and 1. If 1, all samples are used.

    eps : float, optional
        Smallest value of alpha / alpha_max considered

    n_jobs : integer, optional
        Number of CPUs to use during the resampling. If '-1', use
        all the CPUs

    verbose : boolean or integer, optional
        Sets the verbosity amount

    Returns
    -------
    alphas_grid : array, shape ~ [n_grid]
        The grid points between 0 and 1: alpha/alpha_max

    scores_path : array, shape = [n_features, n_grid]
        The scores for each feature along the path.
    """
    X, y = check_X_y(X, y, accept_sparse=['csr', 'csc', 'coo'])
    rng = check_random_state(random_state)

    if not (0 < scaling < 1):
        raise ValueError("Parameter 'scaling' should be between 0 and 1."
                         " Got %r instead." % scaling)

    n_samples, n_features = X.shape

    paths = Parallel(n_jobs=n_jobs, verbose=verbose)(
        delayed(_lasso_stability_path)(
            X, y, mask=rng.rand(n_samples) < sample_fraction,
            weights=1. - scaling * rng.randint(0, 2, size=(n_features,)),
            eps=eps)
        for k in range(n_resampling))

    all_alphas = sorted(list(set(itertools.chain(*[p[0] for p in paths]))))
    # Take approximately n_grid values
    stride = int(max(1, int(len(all_alphas) / float(n_grid))))
    all_alphas = all_alphas[::stride]
    if not all_alphas[-1] == 1:
        all_alphas.append(1.)
    all_alphas = np.array(all_alphas)
    scores_path = np.zeros((n_features, len(all_alphas)))

    for alphas, coefs in paths:
        if alphas[0] != 0:
            alphas = np.r_[0, alphas]
            coefs = np.c_[np.ones((n_features, 1)), coefs]
        if alphas[-1] != all_alphas[-1]:
            alphas = np.r_[alphas, all_alphas[-1]]
            coefs = np.c_[coefs, np.zeros((n_features, 1))]
        scores_path += (interp1d(alphas, coefs,
                        kind='nearest', bounds_error=False,
                        fill_value=0, axis=-1)(all_alphas) != 0)

    scores_path /= n_resampling
    return all_alphas, scores_path