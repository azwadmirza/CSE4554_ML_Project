def truncate(self, before=None, after=None, copy=True):
    """Function truncate a sorted DataFrame / Series before and/or after
    some particular dates.

    Parameters
    ----------
    before : date
        Truncate before date
    after : date
        Truncate after date

    Returns
    -------
    truncated : type of caller
    """
    from pandas.tseries.tools import to_datetime
    before = to_datetime(before)
    after = to_datetime(after)

    if before is not None and after is not None:
        assert(before <= after)

    result = self.ix[before:after]

    if isinstance(self.index, MultiIndex):
        result.index = self.index.truncate(before, after)

    if copy:
        result = result.copy()

    return result