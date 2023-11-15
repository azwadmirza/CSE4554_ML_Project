def pacf(x, nlags=None, method="ywadjusted", alpha=None):
    """
    Partial autocorrelation estimate.

    Parameters
    ----------
    x : array_like
        Observations of time series for which pacf is calculated.
    nlags : int
        The largest lag for which the pacf is returned. The default
        is currently 40, but will change to
        min(int(10 * np.log10(nobs)), nobs // 2 - 1) in the future
    method : str, default "ywunbiased"
        Specifies which method for the calculations to use.

        - "yw" or "ywadjusted" : Yule-Walker with sample-size adjustment in
          denominator for acovf. Default.
        - "ywm" or "ywmle" : Yule-Walker without adjustment.
        - "ols" : regression of time series on lags of it and on constant.
        - "ols-inefficient" : regression of time series on lags using a single
          common sample to estimate all pacf coefficients.
        - "ols-adjusted" : regression of time series on lags with a bias
          adjustment.
        - "ld" or "ldadjusted" : Levinson-Durbin recursion with bias
          correction.
        - "ldb" or "ldbiased" : Levinson-Durbin recursion without bias
          correction.

    alpha : float, optional
        If a number is given, the confidence intervals for the given level are
        returned. For instance if alpha=.05, 95 % confidence intervals are
        returned where the standard deviation is computed according to
        1/sqrt(len(x)).

    Returns
    -------
    pacf : ndarray
        Partial autocorrelations, nlags elements, including lag zero.
    confint : ndarray, optional
        Confidence intervals for the PACF. Returned if confint is not None.

    See Also
    --------
    statsmodels.tsa.stattools.acf
        Estimate the autocorrelation function.
    statsmodels.tsa.stattools.pacf
        Partial autocorrelation estimation.
    statsmodels.tsa.stattools.pacf_yw
         Partial autocorrelation estimation using Yule-Walker.
    statsmodels.tsa.stattools.pacf_ols
        Partial autocorrelation estimation using OLS.
    statsmodels.tsa.stattools.pacf_burg
        Partial autocorrelation estimation using Burg"s method.

    Notes
    -----
    Based on simulation evidence across a range of low-order ARMA models,
    the best methods based on root MSE are Yule-Walker (MLW), Levinson-Durbin
    (MLE) and Burg, respectively. The estimators with the lowest bias included
    included these three in addition to OLS and OLS-adjusted.

    Yule-Walker (adjusted) and Levinson-Durbin (adjusted) performed
    consistently worse than the other options.
    """
    nlags = int_like(nlags, "nlags", optional=True)
    renames = {"ydu":"yda",
               "ywu": "ywa",
               "ywunbiased":"ywadjusted",
               "ldunbiased":"ldadjusted",
               "ld_unbiased":"ld_adjusted",
               "ldu":"lda",
               "ols-unbiased":"ols-adjusted"}
    if method in renames:
        warnings.warn(
            f"{method} has been renamed {renames[method]}. After release 0.13, "
            "using the old name will raise.",
            FutureWarning)
        method = renames[method]
    methods = (
        "ols",
        "ols-inefficient",
        "ols-adjusted",
        "yw",
        "ywa",
        "ld",
        "ywadjusted",
        "yw_adjusted",
        "ywm",
        "ywmle",
        "yw_mle",
        "lda",
        "ldadjusted",
        "ld_adjusted",
        "ldb",
        "ldbiased",
        "ld_biased",
    )
    x = array_like(x, "x", maxdim=2)
    method = string_like(method, "method", options=methods)
    alpha = float_like(alpha, "alpha", optional=True)

    if nlags is None:
        warnings.warn(
            "The default number of lags is changing from 40 to"
            "min(int(10 * np.log10(nobs)), nobs // 2 - 1) after 0.12"
            "is released. Set the number of lags to an integer to "
            " silence this warning.",
            FutureWarning,
        )
        nlags = 40
    if nlags >= x.shape[0] // 2:
        raise ValueError(
            "Can only compute partial correlations for lags up to 50% of the "
            f"sample size. The requested nlags {nlags} must be < "
            f"{x.shape[0] // 2}."
        )

    if method in ("ols", "ols-inefficient", "ols-adjusted"):
        efficient = "inefficient" not in method
        adjusted = "adjusted" in method
        ret = pacf_ols(x, nlags=nlags, efficient=efficient, adjusted=adjusted)
    elif method in ("yw", "ywa", "ywadjusted", "yw_adjusted"):
        ret = pacf_yw(x, nlags=nlags, method="adjusted")
    elif method in ("ywm", "ywmle", "yw_mle"):
        ret = pacf_yw(x, nlags=nlags, method="mle")
    elif method in ("ld", "lda", "ldadjusted", "ld_adjusted"):
        acv = acovf(x, adjusted=True, fft=False)
        ld_ = levinson_durbin(acv, nlags=nlags, isacov=True)
        ret = ld_[2]
    # inconsistent naming with ywmle
    else:  # method in ("ldb", "ldbiased", "ld_biased")
        acv = acovf(x, adjusted=False, fft=False)
        ld_ = levinson_durbin(acv, nlags=nlags, isacov=True)
        ret = ld_[2]

    if alpha is not None:
        varacf = 1.0 / len(x)  # for all lags >=1
        interval = stats.norm.ppf(1.0 - alpha / 2.0) * np.sqrt(varacf)
        confint = np.array(lzip(ret - interval, ret + interval))
        confint[0] = ret[0]  # fix confidence interval for lag 0 to varpacf=0
        return ret, confint
    else:
        return ret