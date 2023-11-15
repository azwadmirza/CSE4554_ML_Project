def _alexa_wide_gamut_rgb_inverse_transfer_function(
        value,
        firmware='SUP 3.x',
        method='Linear Scene Exposure Factor',
        EI=800):
    """
    Defines the *ALEXA Wide Gamut* value colourspace inverse transfer function.

    Parameters
    ----------
    value : numeric
        value.
    firmware : unicode, optional
        {'SUP 3.x', 'SUP 2.x'}
        Alexa firmware version.
    method : unicode,  optional
        {'Linear Scene Exposure Factor', 'Normalised Sensor Signal'}
        Conversion method.
    EI : int,  optional
        Ei.

    Returns
    -------
    numeric
        Companded value.
    """

    cut, a, b, c, d, e, f, _ = (
        ALEXA_LOG_C_CURVE_CONVERSION_DATA.get(firmware).get(method).get(EI))

    return ((np.power(10., (value - d) / c) - b) / a
            if value > e * cut + f else
            (value - f) / e)