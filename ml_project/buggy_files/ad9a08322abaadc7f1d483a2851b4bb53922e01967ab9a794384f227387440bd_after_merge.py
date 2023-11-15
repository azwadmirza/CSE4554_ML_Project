def f_regression(X, y, center=True):
    """Univariate linear regression tests.

    Quick linear model for testing the effect of a single regressor,
    sequentially for many regressors.

    This is done in 3 steps:

    1. The regressor of interest and the data are orthogonalized
       wrt constant regressors.
    2. The cross correlation between data and regressors is computed.
    3. It is converted to an F score then to a p-value.

    Parameters
    ----------
    X : {array-like, sparse matrix}  shape = (n_samples, n_features)
        The set of regressors that will tested sequentially.

    y : array of shape(n_samples).
        The data matrix

    center : True, bool,
        If true, X and y will be centered.

    Returns
    -------
    F : array, shape=(n_features,)
        F values of features.

    pval : array, shape=(n_features,)
        p-values of F-scores.

    See also
    --------
    f_classif: ANOVA F-value between labe/feature for classification tasks.
    chi2: Chi-squared stats of non-negative features for classification tasks.
    """
    if issparse(X) and center:
        raise ValueError("center=True only allowed for dense data")
    X, y = check_X_y(X, y, ['csr', 'csc', 'coo'], dtype=np.float)
    if center:
        y = y - np.mean(y)
        X = X.copy('F')  # faster in fortran
        X -= X.mean(axis=0)

    # compute the correlation
    corr = safe_sparse_dot(y, X)
    # XXX could use corr /= row_norms(X.T) here, but the test doesn't pass
    corr /= np.asarray(np.sqrt(safe_sqr(X).sum(axis=0))).ravel()
    corr /= norm(y)

    # convert to p-value
    degrees_of_freedom = y.size - (2 if center else 1)
    F = corr ** 2 / (1 - corr ** 2) * degrees_of_freedom
    pv = stats.f.sf(F, 1, degrees_of_freedom)
    return F, pv