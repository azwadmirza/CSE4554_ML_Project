def tristimulus_weighting_factors_ASTME202211(cmfs, illuminant, shape):
    """
    Returns a table of tristimulus weighting factors for given colour matching
    functions and illuminant using practise *ASTM E2022-11* method [1]_.

    The computed table of tristimulus weighting factors should be used with
    spectral data that has been corrected for spectral bandpass dependence.

    Parameters
    ----------
    cmfs : XYZ_ColourMatchingFunctions
        Standard observer colour matching functions.
    illuminant : SpectralPowerDistribution
        Illuminant spectral power distribution.
    shape : SpectralShape
        Shape used to build the table, only the interval is needed.

    Returns
    -------
    ndarray
        Tristimulus weighting factors table.

    Raises
    ------
    ValueError
        If the colour matching functions or illuminant intervals are not equal
        to 1 nm.

    Warning
    -------
    -   The tables of tristimulus weighting factors are cached in
        :attr:`_TRISTIMULUS_WEIGHTING_FACTORS_CACHE` attribute. Their
        identifier key is defined by the colour matching functions and
        illuminant names along the current shape such as:
        `CIE 1964 10 Degree Standard Observer, A, (360.0, 830.0, 10.0)`
        Considering the above, one should be mindful that using similar colour
        matching functions and illuminant names but with different spectral
        data will lead to unexpected behaviour.

    Notes
    -----
    -   Input colour matching functions and illuminant intervals are expected
        to be equal to 1 nm. If the illuminant data is not available at 1 nm
        interval, it needs to be interpolated using *CIE* recommendations:
        The method developed by *Sprague (1880)* should be used for
        interpolating functions having a uniformly spaced independent variable
        and a *Cubic Spline* method for non-uniformly spaced independent
        variable.

    Examples
    --------
    >>> from colour import (
    ...     CMFS,
    ...     CIE_standard_illuminant_A_function,
    ...     SpectralPowerDistribution,
    ...     SpectralShape)
    >>> cmfs = CMFS['CIE 1964 10 Degree Standard Observer']
    >>> wl = cmfs.shape.range()
    >>> A = SpectralPowerDistribution(
    ...     'A (360, 830, 1)',
    ...     dict(zip(wl, CIE_standard_illuminant_A_function(wl))))
    >>> tristimulus_weighting_factors_ASTME202211(  # doctest: +ELLIPSIS
    ...     cmfs, A, SpectralShape(360, 830, 20))
    array([[ -2.9816934...e-04,  -3.1709762...e-05,  -1.3301218...e-03],
           [ -8.7154955...e-03,  -8.9154168...e-04,  -4.0743684...e-02],
           [  5.9967988...e-02,   5.0203497...e-03,   2.5650183...e-01],
           [  7.7342255...e-01,   7.7983983...e-02,   3.6965732...e+00],
           [  1.9000905...e+00,   3.0370051...e-01,   9.7554195...e+00],
           [  1.9707727...e+00,   8.5528092...e-01,   1.1486732...e+01],
           [  7.1836236...e-01,   2.1457000...e+00,   6.7845806...e+00],
           [  4.2666758...e-02,   4.8985328...e+00,   2.3208000...e+00],
           [  1.5223302...e+00,   9.6471138...e+00,   7.4306714...e-01],
           [  5.6770329...e+00,   1.4460970...e+01,   1.9581949...e-01],
           [  1.2445174...e+01,   1.7474254...e+01,   5.1826979...e-03],
           [  2.0553577...e+01,   1.7583821...e+01,  -2.6512696...e-03],
           [  2.5331538...e+01,   1.4895703...e+01,   0.0000000...e+00],
           [  2.1571157...e+01,   1.0079661...e+01,   0.0000000...e+00],
           [  1.2178581...e+01,   5.0680655...e+00,   0.0000000...e+00],
           [  4.6675746...e+00,   1.8303239...e+00,   0.0000000...e+00],
           [  1.3236117...e+00,   5.1296946...e-01,   0.0000000...e+00],
           [  3.1753258...e-01,   1.2300847...e-01,   0.0000000...e+00],
           [  7.4634128...e-02,   2.9024389...e-02,   0.0000000...e+00],
           [  1.8299016...e-02,   7.1606335...e-03,   0.0000000...e+00],
           [  4.7942065...e-03,   1.8888730...e-03,   0.0000000...e+00],
           [  1.3293045...e-03,   5.2774591...e-04,   0.0000000...e+00],
           [  4.2546928...e-04,   1.7041978...e-04,   0.0000000...e+00],
           [  9.6251115...e-05,   3.8955295...e-05,   0.0000000...e+00]])
    """

    if cmfs.shape.interval != 1:
        raise ValueError('"{0}" shape "interval" must be 1!'.format(cmfs))

    if illuminant.shape.interval != 1:
        raise ValueError(
            '"{0}" shape "interval" must be 1!'.format(illuminant))

    global _TRISTIMULUS_WEIGHTING_FACTORS_CACHE
    if _TRISTIMULUS_WEIGHTING_FACTORS_CACHE is None:
        _TRISTIMULUS_WEIGHTING_FACTORS_CACHE = CaseInsensitiveMapping()

    name_twf = ', '.join((cmfs.name, illuminant.name, str(shape)))
    if name_twf in _TRISTIMULUS_WEIGHTING_FACTORS_CACHE:
        return _TRISTIMULUS_WEIGHTING_FACTORS_CACHE[name_twf]

    Y = cmfs.values
    S = illuminant.values

    W = S[::shape.interval, np.newaxis] * Y[::shape.interval, :]

    # First and last measurement intervals *Lagrange Coefficients*.
    c_c = lagrange_coefficients_ASTME202211(shape.interval, 'boundary')
    # Intermediate measurement intervals *Lagrange Coefficients*.
    c_b = lagrange_coefficients_ASTME202211(shape.interval, 'inner')

    # Total wavelengths count.
    w_c = len(Y)
    # Measurement interval interpolated values count.
    r_c = c_b.shape[0]
    # Last interval first interpolated wavelength.
    w_lif = w_c - (w_c - 1) % shape.interval - 1 - r_c

    # Intervals count.
    i_c = W.shape[0]
    i_cm = i_c - 1

    for i in range(3):
        # First interval.
        for j in range(r_c):
            for k in range(3):
                W[k, i] = W[k, i] + c_c[j, k] * S[j + 1] * Y[j + 1, i]

        # Last interval.
        for j in range(r_c):
            for k in range(i_cm, i_cm - 3, -1):
                W[k, i] = (W[k, i] + c_c[r_c - j - 1, i_cm - k] *
                           S[j + w_lif] * Y[j + w_lif, i])

        # Intermediate intervals.
        for j in range(i_c - 3):
            for k in range(r_c):
                w_i = (r_c + 1) * (j + 1) + 1 + k
                W[j, i] = W[j, i] + c_b[k, 0] * S[w_i] * Y[w_i, i]
                W[j + 1, i] = W[j + 1, i] + c_b[k, 1] * S[w_i] * Y[w_i, i]
                W[j + 2, i] = W[j + 2, i] + c_b[k, 2] * S[w_i] * Y[w_i, i]
                W[j + 3, i] = W[j + 3, i] + c_b[k, 3] * S[w_i] * Y[w_i, i]

        # Extrapolation of potential incomplete interval.
        for j in range(int(w_c - ((w_c - 1) % shape.interval)), w_c, 1):
            W[i_cm, i] = W[i_cm, i] + S[j] * Y[j, i]

    W *= 100 / np.sum(W, axis=0)[1]

    _TRISTIMULUS_WEIGHTING_FACTORS_CACHE[name_twf] = W

    return W