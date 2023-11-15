def ewmcov(arg1, arg2=None, com=None, span=None, halflife=None, min_periods=0,
           bias=False, freq=None, pairwise=None, how=None):
    if arg2 is None:
        arg2 = arg1
        pairwise = True if pairwise is None else pairwise
    elif isinstance(arg2, (int, float)) and com is None:
        com = arg2
        arg2 = arg1
        pairwise = True if pairwise is None else pairwise
    arg1 = _conv_timerule(arg1, freq, how)
    arg2 = _conv_timerule(arg2, freq, how)

    def _get_ewmcov(X, Y):
        mean = lambda x: ewma(x, com=com, span=span, halflife=halflife, min_periods=min_periods)
        return (mean(X * Y) - mean(X) * mean(Y))
    result = _flex_binary_moment(arg1, arg2, _get_ewmcov,
                                 pairwise=bool(pairwise))
    if not bias:
        com = _get_center_of_mass(com, span, halflife)
        result *= (1.0 + 2.0 * com) / (2.0 * com)

    return result