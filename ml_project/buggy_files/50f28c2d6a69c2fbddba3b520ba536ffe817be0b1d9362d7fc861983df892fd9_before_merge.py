def cape_cin(pressure, temperature, dewpt, parcel_profile):
    r"""Calculate CAPE and CIN.

    Calculate the convective available potential energy (CAPE) and convective inhibition (CIN)
    of a given upper air profile and parcel path. CIN is integrated between the surface and
    LFC, CAPE is integrated between the LFC and EL (or top of sounding). Intersection points of
    the measured temperature profile and parcel profile are linearly interpolated.

    Parameters
    ----------
    pressure : `pint.Quantity`
        The atmospheric pressure level(s) of interest, in order from highest to
        lowest pressure.
    temperature : `pint.Quantity`
        The atmospheric temperature corresponding to pressure.
    dewpt : `pint.Quantity`
        The atmospheric dewpoint corresponding to pressure.
    parcel_profile : `pint.Quantity`
        The temperature profile of the parcel.

    Returns
    -------
    `pint.Quantity`
        Convective Available Potential Energy (CAPE).
    `pint.Quantity`
        Convective INhibition (CIN).

    Notes
    -----
    Formula adopted from [Hobbs1977]_.

    .. math:: \text{CAPE} = -R_d \int_{LFC}^{EL} (T_{parcel} - T_{env}) d\text{ln}(p)

    .. math:: \text{CIN} = -R_d \int_{SFC}^{LFC} (T_{parcel} - T_{env}) d\text{ln}(p)


    * :math:`CAPE` Convective available potential energy
    * :math:`CIN` Convective inhibition
    * :math:`LFC` Pressure of the level of free convection
    * :math:`EL` Pressure of the equilibrium level
    * :math:`SFC` Level of the surface or beginning of parcel path
    * :math:`R_d` Gas constant
    * :math:`g` Gravitational acceleration
    * :math:`T_{parcel}` Parcel temperature
    * :math:`T_{env}` Environment temperature
    * :math:`p` Atmospheric pressure

    See Also
    --------
    lfc, el

    """
    # Calculate LFC limit of integration
    lfc_pressure, _ = lfc(pressure, temperature, dewpt,
                          parcel_temperature_profile=parcel_profile)

    # If there is no LFC, no need to proceed.
    if np.isnan(lfc_pressure):
        return 0 * units('J/kg'), 0 * units('J/kg')
    else:
        lfc_pressure = lfc_pressure.magnitude

    # Calculate the EL limit of integration
    el_pressure, _ = el(pressure, temperature, dewpt,
                        parcel_temperature_profile=parcel_profile)

    # No EL and we use the top reading of the sounding.
    if np.isnan(el_pressure):
        el_pressure = pressure[-1].magnitude
    else:
        el_pressure = el_pressure.magnitude

    # Difference between the parcel path and measured temperature profiles
    y = (parcel_profile - temperature).to(units.degK)

    # Estimate zero crossings
    x, y = _find_append_zero_crossings(np.copy(pressure), y)

    # CAPE
    # Only use data between the LFC and EL for calculation
    p_mask = _less_or_close(x.m, lfc_pressure) & _greater_or_close(x.m, el_pressure)
    x_clipped = x[p_mask].magnitude
    y_clipped = y[p_mask].magnitude
    cape = (mpconsts.Rd
            * (np.trapz(y_clipped, np.log(x_clipped)) * units.degK)).to(units('J/kg'))

    # CIN
    # Only use data between the surface and LFC for calculation
    p_mask = _greater_or_close(x.m, lfc_pressure)
    x_clipped = x[p_mask].magnitude
    y_clipped = y[p_mask].magnitude
    cin = (mpconsts.Rd
           * (np.trapz(y_clipped, np.log(x_clipped)) * units.degK)).to(units('J/kg'))

    return cape, cin