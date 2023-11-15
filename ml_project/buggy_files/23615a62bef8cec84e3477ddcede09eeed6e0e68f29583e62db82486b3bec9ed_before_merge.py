def maybe_box_datetimelike(value: Scalar, dtype: Optional[Dtype] = None) -> Scalar:
    """
    Cast scalar to Timestamp or Timedelta if scalar is datetime-like
    and dtype is not object.

    Parameters
    ----------
    value : scalar
    dtype : Dtype, optional

    Returns
    -------
    scalar
    """
    if dtype == object:
        pass
    elif isinstance(value, (np.datetime64, datetime)):
        value = tslibs.Timestamp(value)
    elif isinstance(value, (np.timedelta64, timedelta)):
        value = tslibs.Timedelta(value)

    return value