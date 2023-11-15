def lookup_linke_turbidity(time, latitude, longitude, filepath=None,
                           interp_turbidity=True):
    """
    Look up the Linke Turibidity from the ``LinkeTurbidities.mat``
    data file supplied with pvlib.

    Parameters
    ----------
    time : pandas.DatetimeIndex

    latitude : float

    longitude : float

    filepath : string
        The path to the ``.mat`` file.

    interp_turbidity : bool
        If ``True``, interpolates the monthly Linke turbidity values
        found in ``LinkeTurbidities.mat`` to daily values.

    Returns
    -------
    turbidity : Series
    """

    # The .mat file 'LinkeTurbidities.mat' contains a single 2160 x 4320 x 12
    # matrix of type uint8 called 'LinkeTurbidity'. The rows represent global
    # latitudes from 90 to -90 degrees; the columns represent global longitudes
    # from -180 to 180; and the depth (third dimension) represents months of
    # the year from January (1) to December (12). To determine the Linke
    # turbidity for a position on the Earth's surface for a given month do the
    # following: LT = LinkeTurbidity(LatitudeIndex, LongitudeIndex, month).
    # Note that the numbers within the matrix are 20 * Linke Turbidity,
    # so divide the number from the file by 20 to get the
    # turbidity.

    try:
        import scipy.io
    except ImportError:
        raise ImportError('The Linke turbidity lookup table requires scipy. ' +
                          'You can still use clearsky.ineichen if you ' +
                          'supply your own turbidities.')

    if filepath is None:
        pvlib_path = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(pvlib_path, 'data', 'LinkeTurbidities.mat')

    mat = scipy.io.loadmat(filepath)
    linke_turbidity_table = mat['LinkeTurbidity']

    latitude_index = (
        np.around(_linearly_scale(latitude, 90, -90, 1, 2160))
        .astype(np.int64))
    longitude_index = (
        np.around(_linearly_scale(longitude, -180, 180, 1, 4320))
        .astype(np.int64))

    g = linke_turbidity_table[latitude_index][longitude_index]

    if interp_turbidity:
        # Data covers 1 year.
        # Assume that data corresponds to the value at
        # the middle of each month.
        # This means that we need to add previous Dec and next Jan
        # to the array so that the interpolation will work for
        # Jan 1 - Jan 15 and Dec 16 - Dec 31.
        # Then we map the month value to the day of year value.
        # This is approximate and could be made more accurate.
        g2 = np.concatenate([[g[-1]], g, [g[0]]])
        days = np.linspace(-15, 380, num=14)
        linke_turbidity = pd.Series(np.interp(time.dayofyear, days, g2),
                                    index=time)
    else:
        linke_turbidity = pd.DataFrame(time.month, index=time)
        # apply monthly data
        linke_turbidity = linke_turbidity.apply(lambda x: g[x[0]-1], axis=1)

    linke_turbidity /= 20.

    return linke_turbidity