def arma_innovations(endog, ar_params=None, ma_params=None, sigma2=1,
                     normalize=False, prefix=None):
    """
    Compute innovations using a given ARMA process.

    Parameters
    ----------
    endog : ndarray
        The observed time-series process, may be univariate or multivariate.
    ar_params : ndarray, optional
        Autoregressive parameters.
    ma_params : ndarray, optional
        Moving average parameters.
    sigma2 : ndarray, optional
        The ARMA innovation variance. Default is 1.
    normalize : bool, optional
        Whether or not to normalize the returned innovations. Default is False.
    prefix : str, optional
        The BLAS prefix associated with the datatype. Default is to find the
        best datatype based on given input. This argument is typically only
        used internally.

    Returns
    -------
    innovations : ndarray
        Innovations (one-step-ahead prediction errors) for the given `endog`
        series with predictions based on the given ARMA process. If
        `normalize=True`, then the returned innovations have been "whitened" by
        dividing through by the square root of the mean square error.
    innovations_mse : ndarray
        Mean square error for the innovations.
    """
    # Parameters
    endog = np.array(endog)
    squeezed = endog.ndim == 1
    if squeezed:
        endog = endog[:, None]

    ar_params = np.atleast_1d([] if ar_params is None else ar_params)
    ma_params = np.atleast_1d([] if ma_params is None else ma_params)

    nobs, k_endog = endog.shape
    ar = np.r_[1, -ar_params]
    ma = np.r_[1, ma_params]

    # Get BLAS prefix
    if prefix is None:
        prefix, dtype, _ = find_best_blas_type(
            [endog, ar_params, ma_params, np.array(sigma2)])
    dtype = prefix_dtype_map[prefix]

    # Make arrays contiguous for BLAS calls
    endog = np.asfortranarray(endog, dtype=dtype)
    ar_params = np.asfortranarray(ar_params, dtype=dtype)
    ma_params = np.asfortranarray(ma_params, dtype=dtype)
    sigma2 = dtype(sigma2).item()

    # Get the appropriate functions
    arma_transformed_acovf_fast = getattr(
        _arma_innovations, prefix + 'arma_transformed_acovf_fast')
    arma_innovations_algo_fast = getattr(
        _arma_innovations, prefix + 'arma_innovations_algo_fast')
    arma_innovations_filter = getattr(
        _arma_innovations, prefix + 'arma_innovations_filter')

    # Run the innovations algorithm for ARMA coefficients
    arma_acovf = arima_process.arma_acovf(ar, ma,
                                          sigma2=sigma2, nobs=nobs) / sigma2
    acovf, acovf2 = arma_transformed_acovf_fast(ar, ma, arma_acovf)
    theta, v = arma_innovations_algo_fast(nobs, ar_params, ma_params,
                                          acovf, acovf2)
    v = np.array(v)
    if (np.any(v < 0) or
            not np.isfinite(theta).all() or
            not np.isfinite(v).all()):
        # This is defensive code that is hard to hit
        raise ValueError(NON_STATIONARY_ERROR)

    # Run the innovations filter across each series
    u = []
    for i in range(k_endog):
        u_i = np.array(arma_innovations_filter(endog[:, i], ar_params,
                                               ma_params, theta))
        u.append(u_i)
    u = np.vstack(u).T
    if normalize:
        u /= v[:, None]**0.5

    # Post-processing
    if squeezed:
        u = u.squeeze()

    return u, v