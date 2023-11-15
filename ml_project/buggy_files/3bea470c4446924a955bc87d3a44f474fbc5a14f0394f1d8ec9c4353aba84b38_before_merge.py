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

    it = np.nditer([pressure, temperature, dewpoint, None],
                   op_dtypes=['float', 'float', 'float', 'float'],
                   flags=['buffered'])

    for press, temp, dewp, ret in it:
        press = press * pressure.units
        temp = temp * temperature.units
        dewp = dewp * dewpoint.units
        lcl_pressure, lcl_temperature = lcl(press, temp, dewp)
        moist_adiabat_temperatures = moist_lapse(concatenate([lcl_pressure, press]),
                                                 lcl_temperature)
        ret[...] = moist_adiabat_temperatures[-1].magnitude

    # If we started with a scalar, return a scalar
    if it.operands[3].size == 1:
        return it.operands[3][0] * moist_adiabat_temperatures.units
    return it.operands[3] * moist_adiabat_temperatures.units