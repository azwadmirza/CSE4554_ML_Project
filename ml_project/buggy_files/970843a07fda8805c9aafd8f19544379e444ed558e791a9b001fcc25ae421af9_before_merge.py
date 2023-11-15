def M_to_E(M, ecc):
    """Eccentric anomaly from mean anomaly.

    .. versionadded:: 0.4.0

    Parameters
    ----------
    M : float
        Mean anomaly in radians.
    ecc : float
        Eccentricity.

    Returns
    -------
    E : float
        Eccentric anomaly.

    Notes
    -----
    This uses a Newton iteration on the Kepler equation.

    """
    E0 = M
    E = newton("elliptic", E0, args=(M, ecc))
    return E