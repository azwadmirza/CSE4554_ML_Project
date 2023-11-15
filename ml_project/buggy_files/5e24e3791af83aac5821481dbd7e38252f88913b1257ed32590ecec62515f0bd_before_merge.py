def arithmetic_mean(confirmed_measures):
    """
    This functoin performs the arithmetic mean aggregation on the output obtained from
    the confirmation measure module.

    Args:
    ----
    confirmed_measures : list of calculated confirmation measure on each set in the segmented topics.

    Returns:
    -------
    mean : Arithmetic mean of all the values contained in confirmation measures.
    """
    return np.mean(confirmed_measures)