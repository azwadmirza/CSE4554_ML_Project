def rolling_corr(arg1, arg2=None, window=None, min_periods=None, freq=None,
                 center=False, pairwise=None):
    if window is None and isinstance(arg2, (int, float)):
        window = arg2
        arg2 = arg1
        pairwise = True if pairwise is None else pairwise  # only default unset
    elif arg2 is None:
        arg2 = arg1
        pairwise = True if pairwise is None else pairwise  # only default unset
    arg1 = _conv_timerule(arg1, freq)
    arg2 = _conv_timerule(arg2, freq)
    window = min(window, len(arg1), len(arg2))

    def _get_corr(a, b):
        num = rolling_cov(a, b, window, min_periods, freq=freq,
                          center=center)
        den = (rolling_std(a, window, min_periods, freq=freq,
                           center=center) *
               rolling_std(b, window, min_periods, freq=freq,
                           center=center))
        return num / den
    return _flex_binary_moment(arg1, arg2, _get_corr, pairwise=bool(pairwise))