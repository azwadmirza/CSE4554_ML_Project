def check_X(X, allow_empty=False, enforce_univariate=False, warn_X=False):
    """Validate input data.

    Parameters
    ----------
    X : pd.Series, pd.DataFrame, np.ndarray
    allow_empty : bool, optional (default=False)
        If True, empty `y` raises an error.

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
    if warn_X:
        warnings.warn(
            "Argument X is given but can't be used by model algorithm.", UserWarning
        )

    # Check if pandas series or numpy array
    return check_series(
        X, enforce_univariate=enforce_univariate, allow_empty=allow_empty
    )