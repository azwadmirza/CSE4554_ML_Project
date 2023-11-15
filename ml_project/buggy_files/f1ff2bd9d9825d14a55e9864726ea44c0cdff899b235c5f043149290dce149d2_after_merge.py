def check_y_X(y, X=None, allow_empty=False, allow_constant=True):
    """Validate input data.

    Parameters
    ----------
    y : pd.Series
    X : pd.DataFrame, optional (default=None)
    allow_empty : bool, optional (default=False)
        If True, empty `y` does not raise an error.
    allow_constant : bool, optional (default=True)
        If True, constant `y` does not raise an error.

    Raises
    ------
    ValueError
        If y or X are invalid inputs
    """
    y = check_y(y, allow_empty=allow_empty, allow_constant=allow_constant)

    if X is not None:
        X = check_X(X=X)
        check_equal_time_index(y, X)

    return y, X