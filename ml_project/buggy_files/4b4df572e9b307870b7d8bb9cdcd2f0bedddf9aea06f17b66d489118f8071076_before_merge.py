def moist_lapse(pressure, temperature, reference_pressure=None):
    r"""Calculate the temperature at a level assuming liquid saturation processes.

    This function lifts a parcel starting at `temperature`. The starting pressure can
    be given by `reference_pressure`. Essentially, this function is calculating moist
    pseudo-adiabats.

    Parameters
    ----------
    pressure : `pint.Quantity`
        The atmospheric pressure level(s) of interest
    temperature : `pint.Quantity`
        The starting temperature
    reference_pressure : `pint.Quantity`, optional
        The reference pressure. If not given, it defaults to the first element of the
        pressure array.

    Returns
    -------
    `pint.Quantity`
       The resulting parcel temperature at levels given by `pressure`

    See Also
    --------
    dry_lapse : Calculate parcel temperature assuming dry adiabatic processes
    parcel_profile : Calculate complete parcel profile

    Notes
    -----
    This function is implemented by integrating the following differential
    equation:

    .. math:: \frac{dT}{dP} = \frac{1}{P} \frac{R_d T + L_v r_s}
                                {C_{pd} + \frac{L_v^2 r_s \epsilon}{R_d T^2}}

    This equation comes from [Bakhshaii2013]_.

    Only reliably functions on 1D profiles (not higher-dimension vertical cross sections or
    grids).

    """
    def dt(t, p):
        t = units.Quantity(t, temperature.units)
        p = units.Quantity(p, pressure.units)
        rs = saturation_mixing_ratio(p, t)
        frac = ((mpconsts.Rd * t + mpconsts.Lv * rs)
                / (mpconsts.Cp_d + (mpconsts.Lv * mpconsts.Lv * rs * mpconsts.epsilon
                                    / (mpconsts.Rd * t * t)))).to('kelvin')
        return (frac / p).magnitude

    if reference_pressure is None:
        reference_pressure = pressure[0]

    pressure = pressure.to('mbar')
    reference_pressure = reference_pressure.to('mbar')
    temperature = np.atleast_1d(temperature)

    side = 'left'

    pres_decreasing = (pressure[0] > pressure[-1])
    if pres_decreasing:
        # Everything is easier if pressures are in increasing order
        pressure = pressure[::-1]
        side = 'right'

    ref_pres_idx = np.searchsorted(pressure.m, reference_pressure.m, side=side)

    ret_temperatures = np.empty((0, temperature.shape[0]))

    if reference_pressure > pressure.min():
        # Integrate downward in pressure
        pres_down = np.append(reference_pressure.m, pressure[(ref_pres_idx - 1)::-1].m)
        trace_down = si.odeint(dt, temperature.m.squeeze(), pres_down.squeeze())
        ret_temperatures = np.concatenate((ret_temperatures, trace_down[:0:-1]))

    if reference_pressure < pressure.max():
        # Integrate upward in pressure
        pres_up = np.append(reference_pressure.m, pressure[ref_pres_idx:].m)
        trace_up = si.odeint(dt, temperature.m.squeeze(), pres_up.squeeze())
        ret_temperatures = np.concatenate((ret_temperatures, trace_up[1:]))

    if pres_decreasing:
        ret_temperatures = ret_temperatures[::-1]

    return units.Quantity(ret_temperatures.T.squeeze(), temperature.units)