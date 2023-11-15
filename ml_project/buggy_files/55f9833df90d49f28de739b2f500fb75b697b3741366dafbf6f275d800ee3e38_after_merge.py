def _new_DatetimeIndex(cls, d):
    """ This is called upon unpickling, rather than the default which doesn't have arguments
        and breaks __new__ """

    # data are already in UTC
    # so need to localize
    tz = d.pop('tz',None)

    result = cls.__new__(cls, verify_integrity=False, **d)
    if tz is not None:
        result = result.tz_localize('UTC').tz_convert(tz)
    return result