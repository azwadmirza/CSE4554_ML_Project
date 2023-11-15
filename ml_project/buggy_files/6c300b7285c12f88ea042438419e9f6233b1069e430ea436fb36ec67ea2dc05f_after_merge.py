def ksstat(x, cdf, alternative='two_sided', args=()):
    """
    Calculate statistic for the Kolmogorov-Smirnov test for goodness of fit

    This calculates the test statistic for a test of the distribution G(x) of
    an observed variable against a given distribution F(x). Under the null
    hypothesis the two distributions are identical, G(x)=F(x). The
    alternative hypothesis can be either 'two_sided' (default), 'less'
    or 'greater'. The KS test is only valid for continuous distributions.

    Parameters
    ----------
    x : array_like, 1d
        array of observations
    cdf : string or callable
        string: name of a distribution in scipy.stats
        callable: function to evaluate cdf
    alternative : 'two_sided' (default), 'less' or 'greater'
        defines the alternative hypothesis (see explanation)
    args : tuple, sequence
        distribution parameters for call to cdf


    Returns
    -------
    D : float
        KS test statistic, either D, D+ or D-

    See Also
    --------
    scipy.stats.kstest

    Notes
    -----

    In the one-sided test, the alternative is that the empirical
    cumulative distribution function of the random variable is "less"
    or "greater" than the cumulative distribution function F(x) of the
    hypothesis, G(x)<=F(x), resp. G(x)>=F(x).

    In contrast to scipy.stats.kstest, this function only calculates the
    statistic which can be used either as distance measure or to implement
    case specific p-values.

    """
    nobs = float(len(x))

    if isinstance(cdf, str):
        cdf = getattr(stats.distributions, cdf).cdf
    elif hasattr(cdf, 'cdf'):
        cdf = getattr(cdf, 'cdf')

    x = np.sort(x)
    cdfvals = cdf(x, *args)

    d_plus = (np.arange(1.0, nobs + 1) / nobs - cdfvals).max()
    d_min = (cdfvals - np.arange(0.0, nobs) / nobs).max()
    if alternative == 'greater':
        return d_plus
    elif alternative == 'less':
        return d_min

    return np.max([d_plus, d_min])