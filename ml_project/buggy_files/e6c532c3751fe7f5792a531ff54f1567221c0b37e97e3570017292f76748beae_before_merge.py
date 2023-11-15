def _conv_timerule(arg, time_rule):
    types = (DataFrame, Series)
    if time_rule is not None and isinstance(arg, types):
        # Conform to whatever frequency needed.
        arg = arg.asfreq(time_rule)

    return arg