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
    assert -np.pi <= M <= np.pi
    if ecc < 0.8:
        E0 = M
    else:
        E0 = np.pi * np.sign(M)
    E = newton("elliptic", E0, args=(M, ecc))
    return E