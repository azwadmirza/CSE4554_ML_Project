def _conv_timerule(arg, freq, time_rule):
    if time_rule is not None:
        import warnings
        warnings.warn("time_rule argument is deprecated, replace with freq",
                       FutureWarning)

        freq = time_rule

    types = (DataFrame, Series)
    if freq is not None and isinstance(arg, types):
        # Conform to whatever frequency needed.
        arg = arg.resample(freq)

    return arg