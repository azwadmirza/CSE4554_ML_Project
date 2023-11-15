def log_interpolate_1d(x, xp, *args, **kwargs):
    r"""Interpolates data with logarithmic x-scale over a specified axis.

    Interpolation on a logarithmic x-scale for interpolation values in pressure coordintates.

    Parameters
    ----------
    x : array-like
        1-D array of desired interpolated values.

    xp : array-like
        The x-coordinates of the data points.

    args : array-like
        The data to be interpolated. Can be multiple arguments, all must be the same shape as
        xp.

    axis : int, optional
        The axis to interpolate over. Defaults to 0.

    fill_value: float, optional
        Specify handling of interpolation points out of data bounds. If None, will return
        ValueError if points are out of bounds. Defaults to nan.

    Returns
    -------
    array-like
        Interpolated values for each point with coordinates sorted in ascending order.

    Examples
    --------
     >>> x_log = np.array([1e3, 1e4, 1e5, 1e6])
     >>> y_log = np.log(x_log) * 2 + 3
     >>> x_interp = np.array([5e3, 5e4, 5e5])
     >>> metpy.calc.log_interp(x_interp, x_log, y_log)
     array([20.03438638, 24.63955657, 29.24472675])

    Notes
    -----
    xp and args must be the same shape.

    """
    # Pull out kwargs
    fill_value = kwargs.pop('fill_value', np.nan)
    axis = kwargs.pop('axis', 0)

    # Handle units
    x, xp = _strip_matching_units(x, xp)

    # Log x and xp
    log_x = np.log(x)
    log_xp = np.log(xp)
    return interpolate_1d(log_x, log_xp, *args, axis=axis, fill_value=fill_value)