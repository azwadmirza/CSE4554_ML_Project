def ewmcov(arg1, arg2, com=None, span=None, min_periods=0, bias=False,
           time_rule=None):
    X, Y = _prep_binary(arg1, arg2)

    X = _conv_timerule(X, time_rule)
    Y = _conv_timerule(Y, time_rule)

    mean = lambda x: ewma(x, com=com, span=span, min_periods=min_periods)

    result = (mean(X*Y) - mean(X) * mean(Y))
    com = _get_center_of_mass(com, span)
    if not bias:
        result *= (1.0 + 2.0 * com) / (2.0 * com)

    return result