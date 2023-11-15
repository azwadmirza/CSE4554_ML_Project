def ewmstd(arg, com=None, span=None, min_periods=0, bias=False,
           time_rule=None):
    result = ewmvar(arg, com=com, span=span, time_rule=time_rule,
                    min_periods=min_periods, bias=bias)
    return _zsqrt(result)