def _incremental_weighted_mean_and_var(X, sample_weight,
                                       last_mean,
                                       last_variance,
                                       last_weight_sum):
    """Calculate weighted mean and weighted variance incremental update.

    .. versionadded:: 0.24

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Data to use for mean and variance update.

    sample_weight : array-like of shape (n_samples,) or None
        Sample weights. If None, then samples are equally weighted.

    last_mean : array-like of shape (n_features,)
        Mean before the incremental update.

    last_variance : array-like of shape (n_features,) or None
        Variance before the incremental update.
        If None, variance update is not computed (in case scaling is not
        required).

    last_weight_sum : array-like of shape (n_features,)
        Sum of weights before the incremental update.

    Returns
    -------
    updated_mean : array of shape (n_features,)

    updated_variance : array of shape (n_features,) or None
        If None, only mean is computed.

    updated_weight_sum : array of shape (n_features,)

    Notes
    -----
    NaNs in `X` are ignored.

    `last_mean` and `last_variance` are statistics computed at the last step
    by the function. Both must be initialized to 0.0.
    The mean is always required (`last_mean`) and returned (`updated_mean`),
    whereas the variance can be None (`last_variance` and `updated_variance`).

    For further details on the algorithm to perform the computation in a
    numerically stable way, see [Finch2009]_, Sections 4 and 5.

    References
    ----------
    .. [Finch2009] `Tony Finch,
       "Incremental calculation of weighted mean and variance",
       University of Cambridge Computing Service, February 2009.
       <https://fanf2.user.srcf.net/hermes/doc/antiforgery/stats.pdf>`_

    """
    # last = stats before the increment
    # new = the current increment
    # updated = the aggregated stats
    if sample_weight is None:
        return _incremental_mean_and_var(X, last_mean, last_variance,
                                         last_weight_sum)
    nan_mask = np.isnan(X)
    sample_weight_T = np.reshape(sample_weight, (1, -1))
    # new_weight_sum with shape (n_features,)
    new_weight_sum = \
        _safe_accumulator_op(np.dot, sample_weight_T, ~nan_mask).ravel()
    total_weight_sum = _safe_accumulator_op(np.sum, sample_weight, axis=0)

    X_0 = np.where(nan_mask, 0, X)
    new_mean = np.average(X_0,
                          weights=sample_weight, axis=0).astype(np.float64)
    new_mean *= total_weight_sum / new_weight_sum
    updated_weight_sum = last_weight_sum + new_weight_sum
    updated_mean = (
            (last_weight_sum * last_mean + new_weight_sum * new_mean)
            / updated_weight_sum)

    if last_variance is None:
        updated_variance = None
    else:
        X_0 = np.where(nan_mask, 0, (X-new_mean)**2)
        new_variance =\
            _safe_accumulator_op(
                np.average, X_0, weights=sample_weight, axis=0)
        new_variance *= total_weight_sum / new_weight_sum
        new_term = (
                new_weight_sum *
                (new_variance +
                 (new_mean - updated_mean) ** 2))
        last_term = (
                last_weight_sum *
                (last_variance +
                 (last_mean - updated_mean) ** 2))
        updated_variance = (new_term + last_term) / updated_weight_sum

    return updated_mean, updated_variance, updated_weight_sum