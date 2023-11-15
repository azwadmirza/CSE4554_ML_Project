def check_X(X, allow_empty=False, enforce_univariate=False):
    """Validate input data.

    Parameters
    ----------
    X : pd.Series, pd.DataFrame, np.ndarray
    allow_empty : bool, optional (default=False)
        If True, empty `y` raises an error.
    enforce_univariate : bool, optional (default=False)
        If True, multivariate Z will raise an error.
    Returns
    -------
    y : pd.Series, pd.DataFrame
        Validated input data.

    Raises
    ------
    ValueError, TypeError
        If y is an invalid input
    UserWarning
        Warning that X is given and model can't use it
    """
    # Check if pandas series or numpy array
    return check_series(
        X,
        enforce_univariate=enforce_univariate,
        allow_empty=allow_empty,
        allow_numpy=False,
    )