def significant_tornado(sbcape, surface_based_lcl_height, storm_helicity_1km, shear_6km):
    r"""Calculate the significant tornado parameter (fixed layer).

    The significant tornado parameter is designed to identify
    environments favorable for the production of significant
    tornadoes contingent upon the development of supercells.
    It's calculated according to the formula used on the SPC
    mesoanalysis page, updated in [Thompson2004]_:

    .. math::  \text{SIGTOR} = \frac{\text{SBCAPE}}{1500 \text{J/kg}} * \frac{(2000 \text{m} -
               \text{LCL}_\text{SB})}{1000 \text{m}} *
               \frac{SRH_{\text{1km}}}{150 \text{m}^\text{s}/\text{s}^2} *
               \frac{\text{Shear}_\text{6km}}{20 \text{m/s}}

    The lcl height is set to zero when the lcl is above 2000m and
    capped at 1 when below 1000m, and the shr6 term is set to 0
    when shr6 is below 12.5 m/s and maxed out at 1.5 when shr6
    exceeds 30 m/s.

    Parameters
    ----------
    sbcape : `pint.Quantity`
        Surface-based CAPE
    surface_based_lcl_height : `pint.Quantity`
        Surface-based lifted condensation level
    storm_helicity_1km : `pint.Quantity`
        Surface-1km storm-relative helicity
    shear_6km : `pint.Quantity`
        Surface-6km bulk shear

    Returns
    -------
    array-like
        significant tornado parameter

    """
    surface_based_lcl_height = np.clip(atleast_1d(surface_based_lcl_height),
                                       1000 * units('meter'), 2000 * units('meter'))
    surface_based_lcl_height[surface_based_lcl_height >
                             2000 * units('meter')] = 0 * units('meter')
    surface_based_lcl_height = ((2000. * units('meter') - surface_based_lcl_height) /
                                (1000. * units('meter')))
    shear_6km = np.clip(atleast_1d(shear_6km), None, 30 * units('m/s'))
    shear_6km[shear_6km < 12.5 * units('m/s')] = 0 * units('m/s')
    shear_6km /= 20 * units('m/s')

    return ((sbcape / (1500. * units('J/kg'))) *
            surface_based_lcl_height *
            (storm_helicity_1km / (150. * units('m^2/s^2'))) * shear_6km)