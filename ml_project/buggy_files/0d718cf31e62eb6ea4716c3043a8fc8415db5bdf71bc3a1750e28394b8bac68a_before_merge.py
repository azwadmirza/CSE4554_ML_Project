def arma_acovf(ar, ma, nobs=10, sigma2=1, dtype=None):
    """
    Theoretical autocovariance function of ARMA process.

    Parameters
    ----------
    ar : array_like, 1d
        The coefficients for autoregressive lag polynomial, including zero lag.
    ma : array_like, 1d
        The coefficients for moving-average lag polynomial, including zero lag.
    nobs : int
        The number of terms (lags plus zero lag) to include in returned acovf.
    sigma2 : float
        Variance of the innovation term.

    Returns
    -------
    ndarray
        The autocovariance of ARMA process given by ar, ma.

    See Also
    --------
    arma_acf : Autocorrelation function for ARMA processes.
    acovf : Sample autocovariance estimation.

    References
    ----------
    .. [*] Brockwell, Peter J., and Richard A. Davis. 2009. Time Series:
        Theory and Methods. 2nd ed. 1991. New York, NY: Springer.
    """
    if dtype is None:
        dtype = np.common_type(np.array(ar), np.array(ma), np.array(sigma2))

    p = len(ar) - 1
    q = len(ma) - 1
    m = max(p, q) + 1

    if sigma2.real < 0:
        raise ValueError('Must have positive innovation variance.')

    # Short-circuit for trivial corner-case
    if p == q == 0:
        out = np.zeros(nobs, dtype=dtype)
        out[0] = sigma2
        return out

    # Get the moving average representation coefficients that we need
    ma_coeffs = arma2ma(ar, ma, lags=m)

    # Solve for the first m autocovariances via the linear system
    # described by (BD, eq. 3.3.8)
    A = np.zeros((m, m), dtype=dtype)
    b = np.zeros((m, 1), dtype=dtype)
    # We need a zero-right-padded version of ar params
    tmp_ar = np.zeros(m, dtype=dtype)
    tmp_ar[:p + 1] = ar
    for k in range(m):
        A[k, :(k + 1)] = tmp_ar[:(k + 1)][::-1]
        A[k, 1:m - k] += tmp_ar[(k + 1):m]
        b[k] = sigma2 * np.dot(ma[k:q + 1], ma_coeffs[:max((q + 1 - k), 0)])
    acovf = np.zeros(max(nobs, m), dtype=dtype)
    acovf[:m] = np.linalg.solve(A, b)[:, 0]

    # Iteratively apply (BD, eq. 3.3.9) to solve for remaining autocovariances
    if nobs > m:
        zi = signal.lfiltic([1], ar, acovf[:m:][::-1])
        acovf[m:] = signal.lfilter([1], ar, np.zeros(nobs - m, dtype=dtype),
                                   zi=zi)[0]

    return acovf[:nobs]