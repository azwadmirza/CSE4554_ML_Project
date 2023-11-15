def el(pressure, temperature, dewpt, parcel_temperature_profile=None):
    r"""Calculate the equilibrium level.

    This works by finding the last intersection of the ideal parcel path and
    the measured environmental temperature. If there is one or fewer intersections, there is
    no equilibrium level.

    Parameters
    ----------
    pressure : `pint.Quantity`
        The atmospheric pressure
    temperature : `pint.Quantity`
        The temperature at the levels given by `pressure`
    dewpt : `pint.Quantity`
        The dew point at the levels given by `pressure`
    parcel_temperature_profile: `pint.Quantity`, optional
        The parcel temperature profile from which to calculate the EL. Defaults to the
        surface parcel profile.

    Returns
    -------
    `pint.Quantity, pint.Quantity`
        The EL pressure and temperature

    See Also
    --------
    parcel_profile

    """
    # Default to surface parcel if no profile or starting pressure level is given
    if parcel_temperature_profile is None:
        parcel_temperature_profile = parcel_profile(pressure, temperature[0],
                                                    dewpt[0]).to('degC')
    # If the top of the sounding parcel is warmer than the environment, there is no EL
    if parcel_temperature_profile[-1] > temperature[-1]:
        return np.nan * pressure.units, np.nan * temperature.units

    # Otherwise the last intersection (as long as there is one) is the EL
    x, y = find_intersections(pressure[1:], parcel_temperature_profile[1:], temperature[1:])
    if len(x) > 0:
        return x[-1], y[-1]
    else:
        return np.nan * pressure.units, np.nan * temperature.units