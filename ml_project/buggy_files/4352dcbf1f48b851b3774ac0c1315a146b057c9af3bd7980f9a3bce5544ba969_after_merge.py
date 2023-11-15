def farnocchia(k, r0, v0, tof):
    r"""Propagates orbit using mean motion.

    This algorithm depends on the geometric shape of the orbit.
    For the case of the strong elliptic or strong hyperbolic orbits:

    ..  math::

        M = M_{0} + \frac{\mu^{2}}{h^{3}}\left ( 1 -e^{2}\right )^{\frac{3}{2}}t

    .. versionadded:: 0.9.0

    Parameters
    ----------
    k : float
        Standar Gravitational parameter
    r0 : ~astropy.units.Quantity
        Initial position vector wrt attractor center.
    v0 : ~astropy.units.Quantity
        Initial velocity vector.
    tof : float
        Time of flight (s).

    Note
    ----
    This method takes initial :math:`\vec{r}, \vec{v}`, calculates classical orbit parameters,
    increases mean anomaly and performs inverse transformation to get final :math:`\vec{r}, \vec{v}`
    The logic is based on formulae (4), (6) and (7) from http://dx.doi.org/10.1007/s10569-013-9476-9

    """

    # get the initial true anomaly and orbit parameters that are constant over time
    p, ecc, inc, raan, argp, nu0 = rv2coe(k, r0, v0)
    q = p / (1 + ecc)

    delta_t0 = delta_t_from_nu(nu0, ecc, k, q)
    delta_t = delta_t0 + tof

    nu = nu_from_delta_t(delta_t, ecc, k, q)

    return coe2rv(k, p, ecc, inc, raan, argp, nu)