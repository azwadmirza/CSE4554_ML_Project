    def __new__(cls, start=None, end=None, periods=None,
                offset=datetools.bday, time_rule=None,
                tzinfo=None, name=None, **kwds):

        import warnings
        warnings.warn("DateRange is deprecated, use DatetimeIndex instead",
                       FutureWarning)

        if time_rule is None:
            time_rule = kwds.get('timeRule')
        if time_rule is not None:
            offset = datetools.get_offset(time_rule)

        return DatetimeIndex(start=start, end=end,
                             periods=periods, freq=offset,
                             tzinfo=tzinfo, name=name, **kwds)