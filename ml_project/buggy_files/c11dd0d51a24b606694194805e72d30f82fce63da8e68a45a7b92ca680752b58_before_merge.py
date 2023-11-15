def mackinnoncrit(
    num_unit_roots: int = 1,
    regression: str = "c",
    nobs: float = inf,
    dist_type: str = "ADF-t",
) -> NDArray:
    """
    Returns the critical values for cointegrating and the ADF test.

    In 2010 MacKinnon updated the values of his 1994 paper with critical values
    for the augmented Dickey-Fuller bootstrap.  These new values are to be
    preferred and are used here.

    Parameters
    ----------
    num_unit_roots : int
        The number of series of I(1) series for which the null of
        non-cointegration is being tested.  For N > 12, the critical values
        are linearly interpolated (not yet implemented).  For the ADF test,
        N = 1.
    regression : {'c', 'tc', 'ctt', 'nc'}, optional
        Following MacKinnon (1996), these stand for the type of regression run.
        'c' for constant and no trend, 'tc' for constant with a linear trend,
        'ctt' for constant with a linear and quadratic trend, and 'nc' for
        no constant.  The values for the no constant case are taken from the
        1996 paper, as they were not updated for 2010 due to the unrealistic
        assumptions that would underlie such a case.
    nobs : {int, np.inf}, optional
        This is the sample size.  If the sample size is numpy.inf, then the
        asymptotic critical values are returned.
    dist_type : {'adf-t', 'adf-z', 'dfgls'}, optional
        Type of test statistic

    Returns
    -------
    crit_vals : ndarray
        Three critical values corresponding to 1%, 5% and 10% cut-offs.

    Notes
    -----
    Results for ADF t-stats from MacKinnon (1994,2010).  Results for DFGLS and
    ADF z-bootstrap use the same methodology as MacKinnon.

    References
    ----------
    MacKinnon, J.G. 1994  "Approximate Asymptotic Distribution Functions for
        Unit-Root and Cointegration Tests." Journal of Business & Economics
        Statistics, 12.2, 167-76.
    MacKinnon, J.G. 2010.  "Critical Values for Cointegration Tests."
        Queen's University, Dept of Economics Working Papers 1227.
        https://ideas.repec.org/p/qed/wpaper/1227.html
    """
    dist_type = dist_type.lower()
    valid_regression = ["c", "ct", "n", "ctt"]
    if dist_type == "dfgls":
        valid_regression = ["c", "ct"]
    if regression not in valid_regression:
        raise ValueError("regression keyword {0} not understood".format(regression))

    if dist_type == "adf-t":
        asymptotic_cv = tau_2010[regression][num_unit_roots - 1, :, 0]
        poly_coef = tau_2010[regression][num_unit_roots - 1, :, :].T
    elif dist_type == "adf-z":
        poly_coef = adf_z_cv_approx[regression].T
        asymptotic_cv = adf_z_cv_approx[regression][:, 0]
    elif dist_type == "dfgls":
        poly_coef = dfgls_cv_approx[regression].T
        asymptotic_cv = dfgls_cv_approx[regression][:, 0]
    else:
        raise ValueError("Unknown test type {0}".format(dist_type))

    if nobs is inf:
        return asymptotic_cv
    else:
        # Flip so that highest power to lowest power
        return polyval(poly_coef[::-1], 1.0 / nobs)