def acf(
    x,
    adjusted=False,
    nlags=None,
    qstat=False,
    fft=None,
    alpha=None,
    missing="none",
):
    """
    Calculate the autocorrelation function.

    Parameters
    ----------
    x : array_like
       The time series data.
    adjusted : bool, default False
       If True, then denominators for autocovariance are n-k, otherwise n.
    nlags : int, default 40
        Number of lags to return autocorrelation for.
    qstat : bool, default False
        If True, returns the Ljung-Box q statistic for each autocorrelation
        coefficient.  See q_stat for more information.
    fft : bool, default None
        If True, computes the ACF via FFT.
    alpha : scalar, default None
        If a number is given, the confidence intervals for the given level are
        returned. For instance if alpha=.05, 95 % confidence intervals are
        returned where the standard deviation is computed according to
        Bartlett"s formula.
    missing : str, default "none"
        A string in ["none", "raise", "conservative", "drop"] specifying how
        the NaNs are to be treated. "none" performs no checks. "raise" raises
        an exception if NaN values are found. "drop" removes the missing
        observations and then estimates the autocovariances treating the
        non-missing as contiguous. "conservative" computes the autocovariance
        using nan-ops so that nans are removed when computing the mean
        and cross-products that are used to estimate the autocovariance.
        When using "conservative", n is set to the number of non-missing
        observations.

    Returns
    -------
    acf : ndarray
        The autocorrelation function.
    confint : ndarray, optional
        Confidence intervals for the ACF. Returned if alpha is not None.
    qstat : ndarray, optional
        The Ljung-Box Q-Statistic.  Returned if q_stat is True.
    pvalues : ndarray, optional
        The p-values associated with the Q-statistics.  Returned if q_stat is
        True.

    Notes
    -----
    The acf at lag 0 (ie., 1) is returned.

    For very long time series it is recommended to use fft convolution instead.
    When fft is False uses a simple, direct estimator of the autocovariances
    that only computes the first nlag + 1 values. This can be much faster when
    the time series is long and only a small number of autocovariances are
    needed.

    If adjusted is true, the denominator for the autocovariance is adjusted
    for the loss of data.

    References
    ----------
    .. [1] Parzen, E., 1963. On spectral analysis with missing observations
       and amplitude modulation. Sankhya: The Indian Journal of
       Statistics, Series A, pp.383-392.
    """
    adjusted = bool_like(adjusted, "adjusted")
    nlags = int_like(nlags, "nlags", optional=True)
    qstat = bool_like(qstat, "qstat")
    fft = bool_like(fft, "fft", optional=True)
    alpha = float_like(alpha, "alpha", optional=True)
    missing = string_like(
        missing, "missing", options=("none", "raise", "conservative", "drop")
    )
    if nlags is None:
        warnings.warn(
            "The default number of lags is changing from 40 to"
            "min(int(10 * np.log10(nobs)), nobs - 1) after 0.12"
            "is released. Set the number of lags to an integer to "
            " silence this warning.",
            FutureWarning,
        )
        nlags = 40

    if fft is None:
        warnings.warn(
            "fft=True will become the default after the release of the 0.12 "
            "release of statsmodels. To suppress this warning, explicitly "
            "set fft=False.",
            FutureWarning,
        )
        fft = False
    x = array_like(x, "x")
    nobs = len(x)  # TODO: should this shrink for missing="drop" and NaNs in x?
    avf = acovf(x, adjusted=adjusted, demean=True, fft=fft, missing=missing)
    acf = avf[: nlags + 1] / avf[0]
    if not (qstat or alpha):
        return acf
    if alpha is not None:
        varacf = np.ones_like(acf) / nobs
        varacf[0] = 0
        varacf[1] = 1.0 / nobs
        varacf[2:] *= 1 + 2 * np.cumsum(acf[1:-1] ** 2)
        interval = stats.norm.ppf(1 - alpha / 2.0) * np.sqrt(varacf)
        confint = np.array(lzip(acf - interval, acf + interval))
        if not qstat:
            return acf, confint
    if qstat:
        qstat, pvalue = q_stat(acf[1:], nobs=nobs)  # drop lag 0
        if alpha is not None:
            return acf, confint, qstat, pvalue
        else:
            return acf, qstat, pvalue