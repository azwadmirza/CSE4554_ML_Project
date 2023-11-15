def decode_cf_datetime(num_dates, units, calendar=None):
    """Given an array of numeric dates in netCDF format, convert it into a
    numpy array of date time objects.

    For standard (Gregorian) calendars, this function uses vectorized
    operations, which makes it much faster than netCDF4.num2date. In such a
    case, the returned array will be of type np.datetime64.

    See also
    --------
    netCDF4.num2date
    """
    import netCDF4 as nc4
    num_dates = np.asarray(num_dates).astype(float)
    if calendar is None:
        calendar = 'standard'

    def nan_safe_num2date(num):
        return pd.NaT if np.isnan(num) else nc4.num2date(num, units, calendar)

    min_num = np.nanmin(num_dates)
    max_num = np.nanmax(num_dates)
    min_date = nan_safe_num2date(min_num)
    if num_dates.size > 1:
        max_date = nan_safe_num2date(max_num)
    else:
        max_date = min_date

    if (calendar not in ['standard', 'gregorian', 'proleptic_gregorian']
            or min_date < datetime(1678, 1, 1)
            or max_date > datetime(2262, 4, 11)):
        dates = nc4.num2date(num_dates, units, calendar)
    else:
        # we can safely use np.datetime64 with nanosecond precision (pandas
        # likes ns precision so it can directly make DatetimeIndex objects)
        if pd.isnull(min_num):
            # pandas.NaT doesn't cast to numpy.datetime64('NaT'), so handle it
            # separately
            dates = np.repeat(np.datetime64('NaT'), num_dates.size)
        elif min_num == max_num:
            # we can't safely divide by max_num - min_num
            dates = np.repeat(np.datetime64(min_date), num_dates.size)
            if dates.size > 1:
                # don't bother with one element, since it will be fixed at
                # min_date and isn't indexable anyways
                dates[np.isnan(num_dates)] = np.datetime64('NaT')
        else:
            # Calculate the date as a np.datetime64 array from linear scaling
            # of the max and min dates calculated via num2date.
            flat_num_dates = num_dates.reshape(-1)
            # Use second precision for the timedelta to decrease the chance of
            # a numeric overflow
            time_delta = np.timedelta64(max_date - min_date).astype('m8[s]')
            if time_delta != max_date - min_date:
                raise ValueError('unable to exactly represent max_date minus'
                                 'min_date with second precision')
            # apply the numerator and denominator separately so we don't need
            # to cast to floating point numbers under the assumption that all
            # dates can be given exactly with ns precision
            numerator = flat_num_dates - min_num
            denominator = max_num - min_num
            dates = (time_delta * numerator / denominator
                     + np.datetime64(min_date))
        # restore original shape and ensure dates are given in ns
        dates = dates.reshape(num_dates.shape).astype('M8[ns]')
    return dates