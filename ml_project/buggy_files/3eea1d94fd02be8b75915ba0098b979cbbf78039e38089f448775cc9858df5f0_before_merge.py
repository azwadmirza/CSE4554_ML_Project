def lfc(pressure, temperature, dewpt, parcel_temperature_profile=None):
    r"""Calculate the level of free convection (LFC).

    This works by finding the first intersection of the ideal parcel path and
    the measured parcel temperature.

    Parameters
    ----------
    pressure : `pint.Quantity`
        The atmospheric pressure
    temperature : `pint.Quantity`
        The temperature at the levels given by `pressure`
    dewpt : `pint.Quantity`
        The dew point at the levels given by `pressure`
    parcel_temperature_profile: `pint.Quantity`, optional
        The parcel temperature profile from which to calculate the LFC. Defaults to the
        surface parcel profile.

    Returns
    -------
    `pint.Quantity`
        The LFC pressure and temperature

    See Also
    --------
    parcel_profile

    """
    # Default to surface parcel if no profile or starting pressure level is given
    if parcel_temperature_profile is None:
        new_stuff = parcel_profile_with_lcl(pressure, temperature, dewpt)
        pressure, temperature, _, parcel_temperature_profile = new_stuff
        temperature = temperature.to('degC')
        parcel_temperature_profile = parcel_temperature_profile.to('degC')

    # The parcel profile and data have the same first data point, so we ignore
    # that point to get the real first intersection for the LFC calculation.
    x, y = find_intersections(pressure[1:], parcel_temperature_profile[1:],
                              temperature[1:], direction='increasing')

    # Compute LCL for this parcel for future comparisons
    this_lcl = lcl(pressure[0], temperature[0], dewpt[0])

    # The LFC could:
    # 1) Not exist
    # 2) Exist but be equal to the LCL
    # 3) Exist and be above the LCL

    # LFC does not exist or is LCL
    if len(x) == 0:
        # Is there any positive area above the LCL?
        mask = pressure < this_lcl[0]
        if np.all(_less_or_close(parcel_temperature_profile[mask], temperature[mask])):
            # LFC doesn't exist
            return np.nan * pressure.units, np.nan * temperature.units
        else:  # LFC = LCL
            x, y = this_lcl
            return x, y

    # LFC exists and is not LCL. Make sure it is above the LCL.
    else:
        idx = x < lcl(pressure[0], temperature[0], dewpt[0])[0]
        x = x[idx]
        y = y[idx]
        return x[0], y[0]