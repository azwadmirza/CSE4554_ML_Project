def storm_relative_helicity(u, v, p, hgt, top, bottom=0 * units('meter'),
                            storm_u=0 * units('m/s'), storm_v=0 * units('m/s')):
    # Partially adapted from similar SharpPy code
    r"""Calculate storm relative helicity.

    Needs u and v wind components, heights and pressures,
    and top and bottom of SRH layer. An optional storm
    motion vector can be specified. SRH is calculated using the
    equation specified on p. 230-231 in the Markowski and Richardson
    meso textbook [Markowski2010].

    .. math:: \int\limits_0^d (\bar v - c) \cdot \bar\omega_{h} \,dz

    This is applied to the data from a hodograph with the following summation:

    .. math:: \sum_{n = 1}^{N-1} [(u_{n+1} - c_{x})(v_{n} - c_{y}) -
                                  (u_{n} - c_{x})(v_{n+1} - c_{y})]

    Parameters
    ----------
    u : array-like
        The u components of winds, same length as hgts
    v : array-like
        The u components of winds, same length as hgts
    p : array-like
        Pressure in hPa, same length as hgts
    hgt : array-like
        The heights associatd with the data, provided in meters above mean
        sea level and converted into meters AGL.
    top : number
        The height of the top of the desired layer for SRH.
    bottom : number
        The height at the bottom of the SRH layer. Default is sfc (None).
    storm_u : number
        u component of storm motion
    storm_v : number
        v component of storm motion

    Returns
    -------
    number
        p_srh : positive storm-relative helicity
    number
        n_srh : negative storm-relative helicity
    number
        t_srh : total storm-relative helicity

    """
    # Converting to m/s to make sure output is in m^2/s^2
    u = u.to('meters/second')
    v = v.to('meters/second')
    storm_u = storm_u.to('meters/second')
    storm_v = storm_v.to('meters/second')

    w_int = get_layer(p, u, v, heights=hgt, bottom=bottom, depth=top - bottom)

    sru = w_int[1] - storm_u
    srv = w_int[2] - storm_v

    int_layers = sru[1:] * srv[:-1] - sru[:-1] * srv[1:]

    p_srh = int_layers[int_layers.magnitude > 0.].sum()
    n_srh = int_layers[int_layers.magnitude < 0.].sum()
    t_srh = p_srh + n_srh

    return p_srh, n_srh, t_srh