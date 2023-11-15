def lcl(pressure, temperature, dewpt, max_iters=50, eps=1e-5):
    r"""Calculate the lifted condensation level (LCL) using from the starting point.

    The starting state for the parcel is defined by `temperature`, `dewpt`,
    and `pressure`.

    Parameters
    ----------
    pressure : `pint.Quantity`
        The starting atmospheric pressure
    temperature : `pint.Quantity`
        The starting temperature
    dewpt : `pint.Quantity`
        The starting dew point

    Returns
    -------
    `(pint.Quantity, pint.Quantity)`
        The LCL pressure and temperature

    Other Parameters
    ----------------
    max_iters : int, optional
        The maximum number of iterations to use in calculation, defaults to 50.
    eps : float, optional
        The desired relative error in the calculated value, defaults to 1e-5.

    See Also
    --------
    parcel_profile

    Notes
    -----
    This function is implemented using an iterative approach to solve for the
    LCL. The basic algorithm is:

    1. Find the dew point from the LCL pressure and starting mixing ratio
    2. Find the LCL pressure from the starting temperature and dewpoint
    3. Iterate until convergence

    The function is guaranteed to finish by virtue of the `max_iters` counter.

    """
    def _lcl_iter(p, p0, w, t):
        td = dewpoint(vapor_pressure(units.Quantity(p, pressure.units), w))
        return (p0 * (td / t) ** (1. / kappa)).m

    w = mixing_ratio(saturation_vapor_pressure(dewpt), pressure)
    fp = so.fixed_point(_lcl_iter, pressure.m, args=(pressure.m, w, temperature),
                        xtol=eps, maxiter=max_iters)
    lcl_p = fp * pressure.units
    return lcl_p, dewpoint(vapor_pressure(lcl_p, w))