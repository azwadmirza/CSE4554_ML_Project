def ewmcorr(arg1, arg2, com=None, span=None, min_periods=0,
            freq=None, time_rule=None):
    X, Y = _prep_binary(arg1, arg2)

    X = _conv_timerule(X, freq, time_rule)
    Y = _conv_timerule(Y, freq, time_rule)

    mean = lambda x: ewma(x, com=com, span=span, min_periods=min_periods)
    var = lambda x: ewmvar(x, com=com, span=span, min_periods=min_periods,
                           bias=True)
    return (mean(X*Y) - mean(X)*mean(Y)) / _zsqrt(var(X) * var(Y))