def wet_bulb_temperature(pressure, temperature, dewpoint):
    """Calculate the wet-bulb temperature using Normand's rule.

    This function calculates the wet-bulb temperature using the Normand method. The LCL is
    computed, and that parcel brought down to the starting pressure along a moist adiabat.
    The Normand method (and others) are described and compared by [Knox2017]_.

    Parameters
    ----------
    pressure : `pint.Quantity`
        Initial atmospheric pressure
    temperature : `pint.Quantity`
        Initial atmospheric temperature
    dewpoint : `pint.Quantity`
        Initial atmospheric dewpoint

    Returns
    -------
    `pint.Quantity`
        Wet-bulb temperature

    See Also
    --------
    lcl, moist_lapse

    Notes
    -----
    Since this function iteratively applies a parcel calculation, it should be used with
    caution on large arrays.

    """
    if not hasattr(pressure, 'shape'):
        pressure = np.atleast_1d(pressure)
        temperature = np.atleast_1d(temperature)
        dewpoint = np.atleast_1d(dewpoint)

    lcl_press, lcl_temp = lcl(pressure, temperature, dewpoint)

    it = np.nditer([pressure.magnitude, lcl_press.magnitude, lcl_temp.magnitude, None],
                   op_dtypes=['float', 'float', 'float', 'float'],
                   flags=['buffered'])

    for press, lpress, ltemp, ret in it:
        press = press * pressure.units
        lpress = lpress * lcl_press.units
        ltemp = ltemp * lcl_temp.units
        moist_adiabat_temperatures = moist_lapse(press, ltemp, lpress)
        ret[...] = moist_adiabat_temperatures.magnitude

    # If we started with a scalar, return a scalar
    ret = it.operands[3]
    if ret.size == 1:
        ret = ret[0]
    return ret * moist_adiabat_temperatures.units