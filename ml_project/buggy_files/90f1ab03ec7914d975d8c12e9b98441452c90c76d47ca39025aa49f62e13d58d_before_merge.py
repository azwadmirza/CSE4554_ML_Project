def _infer_freq(dates):
    if hasattr(dates, "freqstr"):
        return dates.freqstr
    try:
        from pandas.tseries.api import infer_freq
        freq = infer_freq(dates)
        return freq
    except ImportError:
        pass

    timedelta = datetime.timedelta
    nobs = min(len(dates), 6)
    if nobs == 1:
        raise ValueError("Cannot infer frequency from one date")
    if hasattr(dates, 'values'):
        dates = dates.values # can't do a diff on a DateIndex
    diff = np.diff(dates[:nobs])
    delta = _add_datetimes(diff)
    nobs -= 1 # after diff
    if delta == timedelta(nobs): #greedily assume 'D'
        return 'D'
    elif delta == timedelta(nobs + 2):
        return 'B'
    elif delta == timedelta(7*nobs):
        return 'W'
    elif delta >= timedelta(28*nobs) and delta <= timedelta(31*nobs):
        return 'M'
    elif delta >= timedelta(90*nobs) and delta <= timedelta(92*nobs):
        return 'Q'
    elif delta >= timedelta(365 * nobs) and delta <= timedelta(366 * nobs):
        return 'A'
    else:
        return