def _get_bound_pressure_height(pressure, bound, heights=None, interpolate=True):
    """Calculate the bounding pressure and height in a layer.

    Given pressure, optional heights, and a bound, return either the closest pressure/height
    or interpolated pressure/height. If no heights are provided, a standard atmosphere
    ([NOAA1976]_) is assumed.

    Parameters
    ----------
    pressure : `pint.Quantity`
        Atmospheric pressures
    bound : `pint.Quantity`
        Bound to retrieve (in pressure or height)
    heights : `pint.Quantity`, optional
        Atmospheric heights associated with the pressure levels. Defaults to using
        heights calculated from ``pressure`` assuming a standard atmosphere.
    interpolate : boolean, optional
        Interpolate the bound or return the nearest. Defaults to True.

    Returns
    -------
    `pint.Quantity`
        The bound pressure and height.

    """
    # Make sure pressure is monotonically decreasing
    sort_inds = np.argsort(pressure)[::-1]
    pressure = pressure[sort_inds]
    if heights is not None:
        heights = heights[sort_inds]

    # Bound is given in pressure
    if bound.dimensionality == {'[length]': -1.0, '[mass]': 1.0, '[time]': -2.0}:
        # If the bound is in the pressure data, we know the pressure bound exactly
        if bound in pressure:
            bound_pressure = bound
            # If we have heights, we know the exact height value, otherwise return standard
            # atmosphere height for the pressure
            if heights is not None:
                bound_height = heights[pressure == bound_pressure]
            else:
                bound_height = pressure_to_height_std(bound_pressure)
        # If bound is not in the data, return the nearest or interpolated values
        else:
            if interpolate:
                bound_pressure = bound  # Use the user specified bound
                if heights is not None:  # Interpolate heights from the height data
                    bound_height = log_interpolate_1d(bound_pressure, pressure, heights)
                else:  # If not heights given, use the standard atmosphere
                    bound_height = pressure_to_height_std(bound_pressure)
            else:  # No interpolation, find the closest values
                idx = (np.abs(pressure - bound)).argmin()
                bound_pressure = pressure[idx]
                if heights is not None:
                    bound_height = heights[idx]
                else:
                    bound_height = pressure_to_height_std(bound_pressure)

    # Bound is given in height
    elif bound.dimensionality == {'[length]': 1.0}:
        # If there is height data, see if we have the bound or need to interpolate/find nearest
        if heights is not None:
            if bound in heights:  # Bound is in the height data
                bound_height = bound
                bound_pressure = pressure[heights == bound]
            else:  # Bound is not in the data
                if interpolate:
                    bound_height = bound

                    # Need to cast back to the input type since interp (up to at least numpy
                    # 1.13 always returns float64. This can cause upstream users problems,
                    # resulting in something like np.append() to upcast.
                    bound_pressure = (np.interp(np.atleast_1d(bound.m), heights.m,
                                                pressure.m).astype(result_type(bound))
                                      * pressure.units)
                else:
                    idx = (np.abs(heights - bound)).argmin()
                    bound_pressure = pressure[idx]
                    bound_height = heights[idx]
        else:  # Don't have heights, so assume a standard atmosphere
            bound_height = bound
            bound_pressure = height_to_pressure_std(bound)
            # If interpolation is on, this is all we need, if not, we need to go back and
            # find the pressure closest to this and refigure the bounds
            if not interpolate:
                idx = (np.abs(pressure - bound_pressure)).argmin()
                bound_pressure = pressure[idx]
                bound_height = pressure_to_height_std(bound_pressure)

    # Bound has invalid units
    else:
        raise ValueError('Bound must be specified in units of length or pressure.')

    # If the bound is out of the range of the data, we shouldn't extrapolate
    if not (_greater_or_close(bound_pressure, np.nanmin(pressure.m) * pressure.units)
            and _less_or_close(bound_pressure, np.nanmax(pressure.m) * pressure.units)):
        raise ValueError('Specified bound is outside pressure range.')
    if heights is not None and not (_less_or_close(bound_height,
                                                   np.nanmax(heights.m) * heights.units)
                                    and _greater_or_close(bound_height,
                                                          np.nanmin(heights.m)
                                                          * heights.units)):
        raise ValueError('Specified bound is outside height range.')

    return bound_pressure, bound_height