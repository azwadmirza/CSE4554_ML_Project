def acorr_ljungbox(x, lags=None, boxpierce=False):
    '''Ljung-Box test for no autocorrelation

    Parameters
    ----------
    x : array_like, 1d
        data series, regression residuals when used as diagnostic test
    lags : None, int or array_like
        If lags is an integer then this is taken to be the largest lag
        that is included, the test result is reported for all smaller lag length.
        If lags is a list or array, then all lags are included up to the largest
        lag in the list, however only the tests for the lags in the list are
        reported.
        If lags is None, then the default maxlag is 'min((nobs // 2 - 2), 40)'
    boxpierce : {False, True}
        If true, then additional to the results of the Ljung-Box test also the
        Box-Pierce test results are returned

    Returns
    -------
    lbvalue : float or array
        test statistic
    pvalue : float or array
        p-value based on chi-square distribution
    bpvalue : (optionsal), float or array
        test statistic for Box-Pierce test
    bppvalue : (optional), float or array
        p-value based for Box-Pierce test on chi-square distribution

    Notes
    -----
    Ljung-Box and Box-Pierce statistic differ in their scaling of the
    autocorrelation function. Ljung-Box test is reported to have better
    small sample properties.

    TODO: could be extended to work with more than one series
    1d or nd ? axis ? ravel ?
    needs more testing

    ''Verification''

    Looks correctly sized in Monte Carlo studies.
    not yet compared to verified values

    Examples
    --------
    see example script

    References
    ----------
    Greene
    Wikipedia

    '''
    x = np.asarray(x)
    nobs = x.shape[0]
    if lags is None:
        lags = lrange(1, min((nobs // 2 - 2), 40) + 1)
    elif isinstance(lags, (int, long)):
        lags = lrange(1, lags + 1)
    maxlag = lags[-1]
    lags = np.asarray(lags)
    acfx = acf(x, nlags=maxlag) # normalize by nobs not (nobs-nlags)
                             # SS: unbiased=False is default now
    acf2norm = acfx[1:maxlag+1]**2 / (nobs - np.arange(1,maxlag+1))
    qljungbox = nobs * (nobs+2) * np.cumsum(acf2norm)[lags-1]
    pval = stats.chi2.sf(qljungbox, lags)
    if not boxpierce:
        return qljungbox, pval
    else:
        qboxpierce = nobs * np.cumsum(acfx[1:maxlag+1]**2)[lags-1]
        pvalbp = stats.chi2.sf(qboxpierce, lags)
        return qljungbox, pval, qboxpierce, pvalbp