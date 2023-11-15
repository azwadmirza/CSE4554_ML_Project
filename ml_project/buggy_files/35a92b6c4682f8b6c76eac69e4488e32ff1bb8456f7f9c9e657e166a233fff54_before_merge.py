def lfc(pressure, temperature, dewpt, parcel_temperature_profile=None, dewpt_start=None,
        which='top'):
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
        The dewpoint at the levels given by `pressure`
    parcel_temperature_profile: `pint.Quantity`, optional
        The parcel temperature profile from which to calculate the LFC. Defaults to the
        surface parcel profile.
    dewpt_start: `pint.Quantity`, optional
        The dewpoint of the parcel for which to calculate the LFC. Defaults to the surface
        dewpoint.
    which: str, optional
        Pick which LFC to return. Options are 'top', 'bottom', and 'all'.
        Default is the 'top' (lowest pressure) LFC.

    Returns
    -------
    `pint.Quantity`
        The LFC pressure, or array of same if which='all'
    `pint.Quantity`
        The LFC temperature, or array of same if which='all'

    See Also
    --------
    parcel_profile

    """
    # Default to surface parcel if no profile or starting pressure level is given
    if parcel_temperature_profile is None:
        new_stuff = parcel_profile_with_lcl(pressure, temperature, dewpt)
        pressure, temperature, _, parcel_temperature_profile = new_stuff
        parcel_temperature_profile = parcel_temperature_profile.to(temperature.units)

    if dewpt_start is None:
        dewpt_start = dewpt[0]

    # The parcel profile and data may have the same first data point.
    # If that is the case, ignore that point to get the real first
    # intersection for the LFC calculation. Use logarithmic interpolation.
    if np.isclose(parcel_temperature_profile[0].m, temperature[0].m):
        x, y = find_intersections(pressure[1:], parcel_temperature_profile[1:],
                                  temperature[1:], direction='increasing', log_x=True)
    else:
        x, y = find_intersections(pressure, parcel_temperature_profile,
                                  temperature, direction='increasing', log_x=True)

    # Compute LCL for this parcel for future comparisons
    this_lcl = lcl(pressure[0], parcel_temperature_profile[0], dewpt_start)

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
            x, y = np.nan * pressure.units, np.nan * temperature.units
        else:  # LFC = LCL
            x, y = this_lcl
        return x, y

    # LFC exists. Make sure it is no lower than the LCL
    else:
        idx = x < this_lcl[0]
        # LFC height < LCL height, so set LFC = LCL
        if not any(idx):
            el_pres, _ = find_intersections(pressure[1:], parcel_temperature_profile[1:],
                                            temperature[1:], direction='decreasing',
                                            log_x=True)
            if np.min(el_pres) > this_lcl[0]:
                x, y = np.nan * pressure.units, np.nan * temperature.units
            else:
                x, y = this_lcl
            return x, y
        # Otherwise, find all LFCs that exist above the LCL
        # What is returned depends on which flag as described in the docstring
        else:
            return _multiple_el_lfc_options(x, y, idx, which)