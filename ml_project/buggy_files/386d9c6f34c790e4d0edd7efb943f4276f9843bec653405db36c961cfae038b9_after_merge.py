def read_tmy3(filename=None, coerce_year=None, recolumn=True):
    '''
    Read a TMY3 file in to a pandas dataframe.

    Note that values contained in the metadata dictionary are unchanged
    from the TMY3 file (i.e. units are retained). In the case of any
    discrepencies between this documentation and the TMY3 User's Manual
    [1]_, the TMY3 User's Manual takes precedence.

    The TMY3 files were updated in Jan. 2015. This function requires the
    use of the updated files.

    Parameters
    ----------
    filename : None or string, default None
        If None, attempts to use a Tkinter file browser. A string can be
        a relative file path, absolute file path, or url.

    coerce_year : None or int, default None
        If supplied, the year of the index will be set to `coerce_year`, except
        for the last index value which will be set to the *next* year so that
        the index increases monotonically.

    recolumn : bool, default True
        If ``True``, apply standard names to TMY3 columns. Typically this
        results in stripping the units from the column name.

    Returns
    -------
    Tuple of the form (data, metadata).

    data : DataFrame
        A pandas dataframe with the columns described in the table
        below. For more detailed descriptions of each component, please
        consult the TMY3 User's Manual ([1]), especially tables 1-1
        through 1-6.

    metadata : dict
        The site metadata available in the file.

    Notes
    -----
    The returned structures have the following fields.

    ===============   ======  ===================
    key               format  description
    ===============   ======  ===================
    altitude          Float   site elevation
    latitude          Float   site latitudeitude
    longitude         Float   site longitudeitude
    Name              String  site name
    State             String  state
    TZ                Float   UTC offset
    USAF              Int     USAF identifier
    ===============   ======  ===================

    =============================       ======================================================================================================================================================
    TMYData field                       description
    =============================       ======================================================================================================================================================
    TMYData.Index                       A pandas datetime index. NOTE, the index is currently timezone unaware, and times are set to local standard time (daylight savings is not included)
    TMYData.ETR                         Extraterrestrial horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.ETRN                        Extraterrestrial normal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.GHI                         Direct and diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.GHISource                   See [1]_, Table 1-4
    TMYData.GHIUncertainty              Uncertainty based on random and bias error estimates                        see [2]_
    TMYData.DNI                         Amount of direct normal radiation (modeled) recv'd during 60 mintues prior to timestamp, Wh/m^2
    TMYData.DNISource                   See [1]_, Table 1-4
    TMYData.DNIUncertainty              Uncertainty based on random and bias error estimates                        see [2]_
    TMYData.DHI                         Amount of diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.DHISource                   See [1]_, Table 1-4
    TMYData.DHIUncertainty              Uncertainty based on random and bias error estimates                        see [2]_
    TMYData.GHillum                     Avg. total horizontal illuminance recv'd during the 60 minutes prior to timestamp, lx
    TMYData.GHillumSource               See [1]_, Table 1-4
    TMYData.GHillumUncertainty          Uncertainty based on random and bias error estimates                        see [2]_
    TMYData.DNillum                     Avg. direct normal illuminance recv'd during the 60 minutes prior to timestamp, lx
    TMYData.DNillumSource               See [1]_, Table 1-4
    TMYData.DNillumUncertainty          Uncertainty based on random and bias error estimates                        see [2]_
    TMYData.DHillum                     Avg. horizontal diffuse illuminance recv'd during the 60 minutes prior to timestamp, lx
    TMYData.DHillumSource               See [1]_, Table 1-4
    TMYData.DHillumUncertainty          Uncertainty based on random and bias error estimates                        see [2]_
    TMYData.Zenithlum                   Avg. luminance at the sky's zenith during the 60 minutes prior to timestamp, cd/m^2
    TMYData.ZenithlumSource             See [1]_, Table 1-4
    TMYData.ZenithlumUncertainty        Uncertainty based on random and bias error estimates                        see [1]_ section 2.10
    TMYData.TotCld                      Amount of sky dome covered by clouds or obscuring phenonema at time stamp, tenths of sky
    TMYData.TotCldSource                See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.TotCldUncertainty           See [1]_, Table 1-6
    TMYData.OpqCld                      Amount of sky dome covered by clouds or obscuring phenonema that prevent observing the sky at time stamp, tenths of sky
    TMYData.OpqCldSource                See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.OpqCldUncertainty           See [1]_, Table 1-6
    TMYData.DryBulb                     Dry bulb temperature at the time indicated, deg C
    TMYData.DryBulbSource               See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.DryBulbUncertainty          See [1]_, Table 1-6
    TMYData.DewPoint                    Dew-point temperature at the time indicated, deg C
    TMYData.DewPointSource              See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.DewPointUncertainty         See [1]_, Table 1-6
    TMYData.RHum                        Relatitudeive humidity at the time indicated, percent
    TMYData.RHumSource                  See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.RHumUncertainty             See [1]_, Table 1-6
    TMYData.Pressure                    Station pressure at the time indicated, 1 mbar
    TMYData.PressureSource              See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.PressureUncertainty         See [1]_, Table 1-6
    TMYData.Wdir                        Wind direction at time indicated, degrees from north (360 = north; 0 = undefined,calm)
    TMYData.WdirSource                  See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.WdirUncertainty             See [1]_, Table 1-6
    TMYData.Wspd                        Wind speed at the time indicated, meter/second
    TMYData.WspdSource                  See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.WspdUncertainty             See [1]_, Table 1-6
    TMYData.Hvis                        Distance to discernable remote objects at time indicated (7777=unlimited), meter
    TMYData.HvisSource                  See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.HvisUncertainty             See [1]_, Table 1-6
    TMYData.CeilHgt                     Height of cloud base above local terrain (7777=unlimited), meter
    TMYData.CeilHgtSource               See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.CeilHgtUncertainty          See [1]_, Table 1-6
    TMYData.Pwat                        Total precipitable water contained in a column of unit cross section from earth to top of atmosphere, cm
    TMYData.PwatSource                  See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.PwatUncertainty             See [1]_, Table 1-6
    TMYData.AOD                         The broadband aerosol optical depth per unit of air mass due to extinction by aerosol component of atmosphere, unitless
    TMYData.AODSource                   See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.AODUncertainty              See [1]_, Table 1-6
    TMYData.Alb                         The ratio of reflected solar irradiance to global horizontal irradiance, unitless
    TMYData.AlbSource                   See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.AlbUncertainty              See [1]_, Table 1-6
    TMYData.Lprecipdepth                The amount of liquid precipitation observed at indicated time for the period indicated in the liquid precipitation quantity field, millimeter
    TMYData.Lprecipquantity             The period of accumulatitudeion for the liquid precipitation depth field, hour
    TMYData.LprecipSource               See [1]_, Table 1-5, 8760x1 cell array of strings
    TMYData.LprecipUncertainty          See [1]_, Table 1-6
    TMYData.PresWth                     Present weather code, see [2]_.
    TMYData.PresWthSource               Present weather code source, see [2]_.
    TMYData.PresWthUncertainty          Present weather code uncertainty, see [2]_.
    =============================       ======================================================================================================================================================

    .. warning:: TMY3 irradiance data corresponds to the *previous* hour, so
        the first index is 1AM, corresponding to the irradiance from midnight
        to 1AM, and the last index is midnight of the *next* year. For example,
        if the last index in the TMY3 file was 1988-12-31 24:00:00 this becomes
        1989-01-01 00:00:00 after calling :func:`~pvlib.iotools.read_tmy3`.

    .. warning:: When coercing the year, the last index in the dataframe will
        become midnight of the *next* year. For example, if the last index in
        the TMY3 was 1988-12-31 24:00:00, and year is coerced to 1990 then this
        becomes 1991-01-01 00:00:00.

    References
    ----------

    .. [1] Wilcox, S and Marion, W. "Users Manual for TMY3 Data Sets".
       NREL/TP-581-43156, Revised May 2008.

    .. [2] Wilcox, S. (2007). National Solar Radiation Database 1991 2005
       Update: Users Manual. 472 pp.; NREL Report No. TP-581-41364.
    '''

    if filename is None:
        try:
            filename = _interactive_load()
        except ImportError:
            raise ImportError('Interactive load failed. tkinter not supported '
                              'on this system. Try installing X-Quartz and '
                              'reloading')

    head = ['USAF', 'Name', 'State', 'TZ', 'latitude', 'longitude', 'altitude']

    if str(filename).startswith('http'):
        request = Request(filename, headers={'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 '
            'Safari/537.36')})
        response = urlopen(request)
        csvdata = io.StringIO(response.read().decode(errors='ignore'))
    else:
        # assume it's accessible via the file system
        csvdata = open(str(filename), 'r')

    # read in file metadata, advance buffer to second line
    firstline = csvdata.readline()
    if 'Request Rejected' in firstline:
        raise IOError('Remote server rejected TMY file request')

    meta = dict(zip(head, firstline.rstrip('\n').split(",")))

    # convert metadata strings to numeric types
    meta['altitude'] = float(meta['altitude'])
    meta['latitude'] = float(meta['latitude'])
    meta['longitude'] = float(meta['longitude'])
    meta['TZ'] = float(meta['TZ'])
    meta['USAF'] = int(meta['USAF'])

    # use pandas to read the csv file/stringio buffer
    # header is actually the second line in file, but tell pandas to look for
    # header information on the 1st line (0 indexing) because we've already
    # advanced past the true first line with the readline call above.
    data = pd.read_csv(csvdata, header=0)
    # get the date column as a pd.Series of numpy datetime64
    data_ymd = pd.to_datetime(data['Date (MM/DD/YYYY)'], format='%m/%d/%Y')
    # shift the time column so that midnite is 00:00 instead of 24:00
    shifted_hour = data['Time (HH:MM)'].str[:2].astype(int) % 24
    # shift the dates at midnite so they correspond to the next day
    data_ymd[shifted_hour == 0] += datetime.timedelta(days=1)
    # NOTE: as of pandas>=0.24 the pd.Series.array has a month attribute, but
    # in pandas-0.18.1, only DatetimeIndex has month, but indices are immutable
    # so we need to continue to work with the panda series of dates `data_ymd`
    data_index = pd.DatetimeIndex(data_ymd)
    # use indices to check for a leap day and advance it to March 1st
    leapday = (data_index.month == 2) & (data_index.day == 29)
    data_ymd[leapday] += datetime.timedelta(days=1)
    # shifted_hour is a pd.Series, so use pd.to_timedelta to get a pd.Series of
    # timedeltas
    if coerce_year is not None:
        data_ymd = data_ymd.map(lambda dt: dt.replace(year=coerce_year))
        data_ymd.iloc[-1] = data_ymd.iloc[-1].replace(year=coerce_year+1)
    # NOTE: as of pvlib-0.6.3, min req is pandas-0.18.1, so pd.to_timedelta
    # unit must be in (D,h,m,s,ms,us,ns), but pandas>=0.24 allows unit='hour'
    data.index = data_ymd + pd.to_timedelta(shifted_hour, unit='h')

    if recolumn:
        data = _recolumn(data)  # rename to standard column names

    data = data.tz_localize(int(meta['TZ'] * 3600))

    return data, meta