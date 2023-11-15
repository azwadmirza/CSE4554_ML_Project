def _conv_timerule(arg, freq):

    types = (DataFrame, Series)
    if freq is not None and isinstance(arg, types):
        # Conform to whatever frequency needed.
        arg = arg.resample(freq)

    return arg