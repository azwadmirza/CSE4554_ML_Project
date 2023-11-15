def rolling_cov(arg1, arg2=None, window=None, min_periods=None, freq=None,
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

    def _get_cov(X, Y):
        mean = lambda x: rolling_mean(x, window, min_periods, center=center)
        count = rolling_count(X + Y, window, center=center)
        bias_adj = count / (count - 1)
        return (mean(X * Y) - mean(X) * mean(Y)) * bias_adj
    rs = _flex_binary_moment(arg1, arg2, _get_cov, pairwise=bool(pairwise))
    return rs