def _na_for_min_count(
    values: np.ndarray, axis: Optional[int]
) -> Union[Scalar, np.ndarray]:
    """
    Return the missing value for `values`.

    Parameters
    ----------
    values : ndarray
    axis : int or None
        axis for the reduction, required if values.ndim > 1.

    Returns
    -------
    result : scalar or ndarray
        For 1-D values, returns a scalar of the correct missing type.
        For 2-D values, returns a 1-D array where each element is missing.
    """
    # we either return np.nan or pd.NaT
    if is_numeric_dtype(values):
        values = values.astype("float64")
    fill_value = na_value_for_dtype(values.dtype)

    if values.ndim == 1:
        return fill_value
    else:
        assert axis is not None  # assertion to make mypy happy
        result_shape = values.shape[:axis] + values.shape[axis + 1 :]
        result = np.empty(result_shape, dtype=values.dtype)
        result.fill(fill_value)
        return result