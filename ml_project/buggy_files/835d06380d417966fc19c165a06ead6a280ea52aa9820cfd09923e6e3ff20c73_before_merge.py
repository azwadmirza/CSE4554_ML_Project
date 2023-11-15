def fuentes(poa_global, temp_air, wind_speed, noct_installed, module_height=5,
            wind_height=9.144, emissivity=0.84, absorption=0.83,
            surface_tilt=30, module_width=0.31579, module_length=1.2):
    """
    Calculate cell or module temperature using the Fuentes model.

    The Fuentes model is a first-principles heat transfer energy balance
    model [1]_ that is used in PVWatts for cell temperature modeling [2]_.

    Parameters
    ----------
    poa_global : pandas Series
        Total incident irradiance [W/m^2]

    temp_air : pandas Series
        Ambient dry bulb temperature [C]

    wind_speed : pandas Series
        Wind speed [m/s]

    noct_installed : float
        The "installed" nominal operating cell temperature as defined in [1]_.
        PVWatts assumes this value to be 45 C for rack-mounted arrays and
        49 C for roof mount systems with restricted air flow around the
        module.  [C]

    module_height : float, default 5.0
        The height above ground of the center of the module. The PVWatts
        default is 5.0 [m]

    wind_height : float, default 9.144
        The height above ground at which ``wind_speed`` is measured. The
        PVWatts defauls is 9.144 [m]

    emissivity : float, default 0.84
        The effectiveness of the module at radiating thermal energy. [unitless]

    absorption : float, default 0.83
        The fraction of incident irradiance that is converted to thermal
        energy in the module. [unitless]

    surface_tilt : float, default 30
        Module tilt from horizontal. If not provided, the default value
        of 30 degrees from [1]_ and [2]_ is used. [degrees]

    module_width : float, default 0.31579
        Module width. The default value of 0.31579 meters in combination with
        the default `module_length` gives a hydraulic diameter of 0.5 as
        assumed in [1]_ and [2]_. [m]

    module_length : float, default 1.2
        Module length. The default value of 1.2 meters in combination with
        the default `module_width` gives a hydraulic diameter of 0.5 as
        assumed in [1]_ and [2]_. [m]

    Returns
    -------
    temperature_cell : pandas Series
        The modeled cell temperature [C]

    Notes
    -----
    This function returns slightly different values from PVWatts at night
    and just after dawn. This is because the SAM SSC assumes that module
    temperature equals ambient temperature when irradiance is zero so it can
    skip the heat balance calculation at night.

    References
    ----------
    .. [1] Fuentes, M. K., 1987, "A Simplifed Thermal Model for Flat-Plate
           Photovoltaic Arrays", SAND85-0330, Sandia National Laboratories,
           Albuquerque NM.
           http://prod.sandia.gov/techlib/access-control.cgi/1985/850330.pdf
    .. [2] Dobos, A. P., 2014, "PVWatts Version 5 Manual", NREL/TP-6A20-62641,
           National Renewable Energy Laboratory, Golden CO.
           doi:10.2172/1158421.
    """
    # ported from the FORTRAN77 code provided in Appendix A of Fuentes 1987;
    # nearly all variable names are kept the same for ease of comparison.

    boltz = 5.669e-8
    emiss = emissivity
    absorp = absorption
    xlen = _hydraulic_diameter(module_width, module_length)
    # cap0 has units of [J / (m^2 K)], equal to mass per unit area times
    # specific heat of the module.
    cap0 = 11000
    tinoct = noct_installed + 273.15

    # convective coefficient of top surface of module at NOCT
    windmod = 1.0
    tave = (tinoct + 293.15) / 2
    hconv = _fuentes_hconv(tave, windmod, tinoct, tinoct - 293.15, xlen,
                           surface_tilt, False)

    # determine the ground temperature ratio and the ratio of the total
    # convection to the top side convection
    hground = emiss * boltz * (tinoct**2 + 293.15**2) * (tinoct + 293.15)
    backrat = (
        absorp * 800.0
        - emiss * boltz * (tinoct**4 - 282.21**4)
        - hconv * (tinoct - 293.15)
    ) / ((hground + hconv) * (tinoct - 293.15))
    tground = (tinoct**4 - backrat * (tinoct**4 - 293.15**4))**0.25
    tground = np.clip(tground, 293.15, tinoct)

    tgrat = (tground - 293.15) / (tinoct - 293.15)
    convrat = (absorp * 800 - emiss * boltz * (
        2 * tinoct**4 - 282.21**4 - tground**4)) / (hconv * (tinoct - 293.15))

    # adjust the capacitance (thermal mass) of the module based on the INOCT.
    # It is a function of INOCT because high INOCT implies thermal coupling
    # with the racking (e.g. roofmount), so the thermal mass is increased.
    # `cap` has units J/(m^2 C) -- see Table 3, Equations 26 & 27
    cap = cap0
    if tinoct > 321.15:
        cap = cap * (1 + (tinoct - 321.15) / 12)

    # iterate through timeseries inputs
    sun0 = 0
    tmod0 = 293.15

    # n.b. the way Fuentes calculates the first timedelta makes it seem like
    # the value doesn't matter -- rather than recreate it here, just assume
    # it's the same as the second timedelta:
    timedelta_hours = np.diff(poa_global.index).astype(float) / 1e9 / 60 / 60
    timedelta_hours = np.append([timedelta_hours[0]], timedelta_hours)

    tamb_array = temp_air + 273.15
    sun_array = poa_global * absorp

    # Two of the calculations are easily vectorized, so precalculate them:
    # sky temperature -- Equation 24
    tsky_array = 0.68 * (0.0552 * tamb_array**1.5) + 0.32 * tamb_array
    # wind speed at module height -- Equation 22
    # not sure why the 1e-4 factor is included -- maybe the equations don't
    # behave well if wind == 0?
    windmod_array = wind_speed * (module_height/wind_height)**0.2 + 1e-4

    tmod0 = 293.15
    tmod_array = np.zeros_like(poa_global)

    iterator = zip(tamb_array, sun_array, windmod_array, tsky_array,
                   timedelta_hours)
    for i, (tamb, sun, windmod, tsky, dtime) in enumerate(iterator):
        # solve the heat transfer equation, iterating because the heat loss
        # terms depend on tmod. NB Fuentes doesn't show that 10 iterations is
        # sufficient for convergence.
        tmod = tmod0
        for j in range(10):
            # overall convective coefficient
            tave = (tmod + tamb) / 2
            hconv = convrat * _fuentes_hconv(tave, windmod, tinoct,
                                             abs(tmod-tamb), xlen,
                                             surface_tilt, True)
            # sky radiation coefficient (Equation 3)
            hsky = emiss * boltz * (tmod**2 + tsky**2) * (tmod + tsky)
            # ground radiation coeffieicient (Equation 4)
            tground = tamb + tgrat * (tmod - tamb)
            hground = emiss * boltz * (tmod**2 + tground**2) * (tmod + tground)
            # thermal lag -- Equation 8
            eigen = - (hconv + hsky + hground) / cap * dtime * 3600
            # not sure why this check is done, maybe as a speed optimization?
            if eigen > -10:
                ex = np.exp(eigen)
            else:
                ex = 0
            # Equation 7 -- note that `sun` and `sun0` already account for
            # absorption (alpha)
            tmod = tmod0 * ex + (
                (1 - ex) * (
                    hconv * tamb
                    + hsky * tsky
                    + hground * tground
                    + sun0
                    + (sun - sun0) / eigen
                ) + sun - sun0
            ) / (hconv + hsky + hground)
        tmod_array[i] = tmod
        tmod0 = tmod
        sun0 = sun

    return pd.Series(tmod_array - 273.15, index=poa_global.index, name='tmod')