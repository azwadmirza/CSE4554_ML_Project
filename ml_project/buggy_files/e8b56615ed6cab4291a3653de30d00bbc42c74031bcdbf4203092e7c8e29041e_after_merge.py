def surface_based_cape_cin(pressure, temperature, dewpoint):
    r"""Calculate surface-based CAPE and CIN.

    Calculate the convective available potential energy (CAPE) and convective inhibition (CIN)
    of a given upper air profile for a surface-based parcel. CIN is integrated
    between the surface and LFC, CAPE is integrated between the LFC and EL (or top of
    sounding). Intersection points of the measured temperature profile and parcel profile are
    linearly interpolated.

    Parameters
    ----------
    pressure : `pint.Quantity`
        Atmospheric pressure profile. The first entry should be the starting
        (surface) observation.
    temperature : `pint.Quantity`
        Temperature profile
    dewpoint : `pint.Quantity`
        Dewpoint profile

    Returns
    -------
    `pint.Quantity`
        Surface based Convective Available Potential Energy (CAPE).
    `pint.Quantity`
        Surface based Convective INhibition (CIN).

    See Also
    --------
    cape_cin, parcel_profile

    """
    p, t, td, profile = parcel_profile_with_lcl(pressure, temperature, dewpoint)
    return cape_cin(p, t, td, profile)