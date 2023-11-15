def reconstruct_object(flags, value):
    """ Reconstructs the value (if necessary) after having saved it in a
    dictionary
    """
    if not isinstance(flags, list):
        flags = parse_flag_string(flags)
    if 'sig' in flags:
        if isinstance(value, dict):
            from hyperspy.signal import Signal
            value = Signal(**value)
            value._assign_subclass()
        return value
    if 'fn' in flags:
        ifdill, thing = value
        if ifdill is None:
            return thing
        if ifdill in [False, 'False', b'False']:
            return types.FunctionType(marshal.loads(thing), globals())
        if ifdill in [True, 'True', b'True']:
            if not dill_avail:
                raise ValueError("the dictionary was constructed using "
                                 "\"dill\" package, which is not available on the system")
            else:
                return dill.loads(thing)
        # should not be reached
        raise ValueError("The object format is not recognized")
    return value