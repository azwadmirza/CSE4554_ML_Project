def _resample_model(estimator_func, X, y, scaling=.5, n_resampling=200,
                    n_jobs=1, verbose=False, pre_dispatch='3*n_jobs',
                    random_state=None, sample_fraction=.75, **params):
    random_state = check_random_state(random_state)
    # We are generating 1 - weights, and not weights
    n_samples, n_features = X.shape

    if not (0 < scaling < 1):
        raise ValueError(
            "'scaling' should be between 0 and 1. Got %r instead." % scaling)

    scaling = 1. - scaling
    scores_ = 0.0
    for active_set in Parallel(n_jobs=n_jobs, verbose=verbose,
                               pre_dispatch=pre_dispatch)(
            delayed(estimator_func)(
                X, y, weights=scaling * random_state.random_integers(
                    0, 1, size=(n_features,)),
                mask=(random_state.rand(n_samples) < sample_fraction),
                verbose=max(0, verbose - 1),
                **params)
            for _ in range(n_resampling)):
        scores_ += active_set.astype(np.float)

    scores_ /= n_resampling
    return scores_