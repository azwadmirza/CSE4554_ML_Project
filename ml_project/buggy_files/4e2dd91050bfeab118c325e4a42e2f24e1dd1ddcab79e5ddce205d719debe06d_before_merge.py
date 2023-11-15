def simultaneous_ci(q_crit, var, groupnobs, pairindices=None):
    """Compute simultaneous confidence intervals for comparison of means.

    q_crit value is generated from tukey hsd test. Variance is considered
    across all groups. Returned halfwidths can be thought of as uncertainty
    intervals around each group mean. They allow for simultaneous
    comparison of pairwise significance among any pairs (by checking for
    overlap)

    Parameters
    ----------
    q_crit : float
        The Q critical value studentized range statistic from Tukey's HSD
    var : float
        The group variance
    groupnobs : array-like object
        Number of observations contained in each group.
    pairindices : tuple of lists, optional
        Indices corresponding to the upper triangle of matrix. Computed
        here if not supplied

    Returns
    -------
    halfwidths : ndarray
        Half the width of each confidence interval for each group given in
        groupnobs

    See Also
    --------
    MultiComparison : statistics class providing significance tests
    tukeyhsd : among other things, computes q_crit value

    References
    ----------
    .. [1] Hochberg, Y., and A. C. Tamhane. Multiple Comparison Procedures.
           Hoboken, NJ: John Wiley & Sons, 1987.)
    """
    # Set initial variables
    ng = len(groupnobs)
    if pairindices is None:
        pairindices = np.triu_indices(ng, 1)

    # Compute dij for all pairwise comparisons ala hochberg p. 95
    gvar = var / groupnobs

    d12 = np.sqrt(gvar[pairindices[0]] + gvar[pairindices[1]])

    # Create the full d matrix given all known dij vals
    d = np.zeros((ng, ng))
    d[pairindices] = d12
    d = d + d.conj().T

    # Compute the two global sums from hochberg eq 3.32
    sum1 = np.sum(d12)
    sum2 = np.sum(d, axis=0)

    if (ng > 2):
        w = ((ng-1.) * sum2 - sum1) / ((ng - 1.) * (ng - 2.))
    else:
        w = sum1 * ones(2, 1) / 2.

    return (q_crit / np.sqrt(2))*w