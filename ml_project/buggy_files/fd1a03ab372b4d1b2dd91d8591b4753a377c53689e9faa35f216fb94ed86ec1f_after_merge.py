def pval_lf(d_max, n):
    """
    Approximate pvalues for Lilliefors test

    This is only valid for pvalues smaller than 0.1 which is not checked in
    this function.

    Parameters
    ----------
    d_max : array_like
        two-sided Kolmogorov-Smirnov test statistic
    n : int or float
        sample size

    Returns
    -------
    p-value : float or ndarray
        pvalue according to approximation formula of Dallal and Wilkinson.

    Notes
    -----
    This is mainly a helper function where the calling code should dispatch
    on bound violations. Therefore it doesn't check whether the pvalue is in
    the valid range.

    Precision for the pvalues is around 2 to 3 decimals. This approximation is
    also used by other statistical packages (e.g. R:fBasics) but might not be
    the most precise available.

    References
    ----------
    DallalWilkinson1986
    """
    # todo: check boundaries, valid range for n and Dmax
    if n > 100:
        d_max *= (n / 100.) ** 0.49
        n = 100
    pval = np.exp(-7.01256 * d_max ** 2 * (n + 2.78019)
                  + 2.99587 * d_max * np.sqrt(n + 2.78019) - 0.122119
                  + 0.974598 / np.sqrt(n) + 1.67997 / n)
    return pval