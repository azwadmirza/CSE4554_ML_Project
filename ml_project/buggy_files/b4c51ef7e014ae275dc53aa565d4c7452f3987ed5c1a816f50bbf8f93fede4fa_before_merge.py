def _attempt_YYYYMMDD(arg, errors):
    """
    try to parse the YYYYMMDD/%Y%m%d format, try to deal with NaT-like,
    arg is a passed in as an object dtype, but could really be ints/strings
    with nan-like/or floats (e.g. with nan)

    Parameters
    ----------
    arg : passed value
    errors : 'raise','ignore','coerce'
    """

    def calc(carg):
        # calculate the actual result
        carg = carg.astype(object)
        parsed = parsing.try_parse_year_month_day(
            carg / 10000, carg / 100 % 100, carg % 100
        )
        return tslib.array_to_datetime(parsed, errors=errors)[0]

    def calc_with_mask(carg, mask):
        result = np.empty(carg.shape, dtype="M8[ns]")
        iresult = result.view("i8")
        iresult[~mask] = tslibs.iNaT

        masked_result = calc(carg[mask].astype(np.float64).astype(np.int64))
        result[mask] = masked_result.astype("M8[ns]")
        return result

    # try intlike / strings that are ints
    try:
        return calc(arg.astype(np.int64))
    except (ValueError, OverflowError):
        pass

    # a float with actual np.nan
    try:
        carg = arg.astype(np.float64)
        return calc_with_mask(carg, notna(carg))
    except (ValueError, OverflowError):
        pass

    # string with NaN-like
    try:
        mask = ~algorithms.isin(arg, list(tslib.nat_strings))
        return calc_with_mask(arg, mask)
    except (ValueError, OverflowError):
        pass

    return None