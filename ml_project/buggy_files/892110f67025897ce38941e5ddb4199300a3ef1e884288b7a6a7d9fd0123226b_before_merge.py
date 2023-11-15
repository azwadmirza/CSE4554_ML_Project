def ewmcorr(arg1, arg2=None, com=None, span=None, halflife=None, min_periods=0,
            freq=None, pairwise=None):
    if arg2 is None:
        arg2 = arg1
        pairwise = True if pairwise is None else pairwise
    elif isinstance(arg2, (int, float)) and com is None:
        com = arg2
        arg2 = arg1
        pairwise = True if pairwise is None else pairwise
    arg1 = _conv_timerule(arg1, freq)
    arg2 = _conv_timerule(arg2, freq)

    def _get_ewmcorr(X, Y):
        mean = lambda x: ewma(x, com=com, span=span, halflife=halflife, min_periods=min_periods)
        var = lambda x: ewmvar(x, com=com, span=span, halflife=halflife, min_periods=min_periods,
                               bias=True)
        return (mean(X * Y) - mean(X) * mean(Y)) / _zsqrt(var(X) * var(Y))
    result = _flex_binary_moment(arg1, arg2, _get_ewmcorr,
                                 pairwise=bool(pairwise))
    return result