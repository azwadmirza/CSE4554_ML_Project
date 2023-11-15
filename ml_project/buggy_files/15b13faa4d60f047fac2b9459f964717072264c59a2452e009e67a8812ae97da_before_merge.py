def ewma(arg, com=None, span=None, min_periods=0, freq=None, time_rule=None):
    com = _get_center_of_mass(com, span)
    arg = _conv_timerule(arg, freq, time_rule)

    def _ewma(v):
        result = _tseries.ewma(v, com)
        first_index = _first_valid_index(v)
        result[first_index : first_index + min_periods] = NaN
        return result

    return_hook, values = _process_data_structure(arg)
    output = np.apply_along_axis(_ewma, 0, values)
    return return_hook(output)