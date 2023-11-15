def _match_types(arg1, arg2):
    if (isinstance(arg1, float) or isinstance(arg1, int)) and isinstance(arg2, tuple):
        arg1_tuple = (arg1, arg1)
        return arg1_tuple, arg2
    if (isinstance(arg2, float) or isinstance(arg2, int)) and isinstance(arg1, tuple):
        arg2_tuple = (arg2, arg2)
        return arg1, arg2_tuple
    return arg1, arg2