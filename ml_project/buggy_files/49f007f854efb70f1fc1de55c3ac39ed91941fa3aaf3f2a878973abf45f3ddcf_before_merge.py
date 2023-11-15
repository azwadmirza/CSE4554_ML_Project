def _convert_datetimes(sas_datetimes: pd.Series, unit: str) -> pd.Series:
    """
    Convert to Timestamp if possible, otherwise to datetime.datetime.
    SAS float64 lacks precision for more than ms resolution so the fit
    to datetime.datetime is ok.

    Parameters
    ----------
    sas_datetimes : {Series, Sequence[float]}
       Dates or datetimes in SAS
    unit : {str}
       "d" if the floats represent dates, "s" for datetimes

    Returns
    -------
    Series
       Series of datetime64 dtype or datetime.datetime.
    """
    try:
        return pd.to_datetime(sas_datetimes, unit=unit, origin="1960-01-01")
    except OutOfBoundsDatetime:
        if unit == "s":
            s_series = sas_datetimes.apply(
                lambda sas_float: datetime(1960, 1, 1) + timedelta(seconds=sas_float)
            )
            s_series = cast(pd.Series, s_series)
            return s_series
        elif unit == "d":
            d_series = sas_datetimes.apply(
                lambda sas_float: datetime(1960, 1, 1) + timedelta(days=sas_float)
            )
            d_series = cast(pd.Series, d_series)
            return d_series
        else:
            raise ValueError("unit must be 'd' or 's'")