def supercell_composite(mucape, effective_storm_helicity, effective_shear):
    r"""Calculate the supercell composite parameter.

    The supercell composite parameter is designed to identify
    environments favorable for the development of supercells,
    and is calculated using the formula developed by
    [Thompson2004]_:

    .. math::  \text{SCP} = \frac{\text{MUCAPE}}{1000 \text{J/kg}} *
               \frac{\text{Effective SRH}}{50 \text{m}^2/\text{s}^2} *
               \frac{\text{Effective Shear}}{20 \text{m/s}}

    The effective_shear term is set to zero below 10 m/s and
    capped at 1 when effective_shear exceeds 20 m/s.

    Parameters
    ----------
    mucape : `pint.Quantity`
        Most-unstable CAPE
    effective_storm_helicity : `pint.Quantity`
        Effective-layer storm-relative helicity
    effective_shear : `pint.Quantity`
        Effective bulk shear

    Returns
    -------
    array-like
        supercell composite

    """
    effective_shear = np.clip(atleast_1d(effective_shear), None, 20 * units('m/s'))
    effective_shear[effective_shear < 10 * units('m/s')] = 0 * units('m/s')
    effective_shear = effective_shear / (20 * units('m/s'))

    return ((mucape / (1000 * units('J/kg'))) *
            (effective_storm_helicity / (50 * units('m^2/s^2'))) *
            effective_shear).to('dimensionless')