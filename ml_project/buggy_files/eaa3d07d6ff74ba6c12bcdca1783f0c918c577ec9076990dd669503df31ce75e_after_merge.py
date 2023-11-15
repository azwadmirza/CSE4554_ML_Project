def ewma(arg, com=None, span=None, halflife=None, min_periods=0, freq=None,
         adjust=True, how=None):
    com = _get_center_of_mass(com, span, halflife)
    arg = _conv_timerule(arg, freq, how)

    def _ewma(v):
        result = algos.ewma(v, com, int(adjust))
        first_index = _first_valid_index(v)
        result[first_index: first_index + min_periods] = NaN
        return result

    return_hook, values = _process_data_structure(arg)
    output = np.apply_along_axis(_ewma, 0, values)
    return return_hook(output)