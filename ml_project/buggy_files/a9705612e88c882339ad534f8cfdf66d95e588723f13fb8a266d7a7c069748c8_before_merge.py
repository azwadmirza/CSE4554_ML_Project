def reconstruct_object(flags, value):
    """ Reconstructs the value (if necessary) after having saved it in a
    dictionary
    """
    if not isinstance(flags, list):
        flags = parse_flag_string(flags)
    if 'sig' in flags:
        if isinstance(value, dict):
            from hyperspy.signal import BaseSignal
            value = BaseSignal(**value)
            value._assign_subclass()
        return value
    if 'fn' in flags:
        ifdill, thing = value
        if ifdill is None:
            return thing
        if ifdill in [True, 'True', b'True']:
            return dill.loads(thing)
        # should not be reached
        raise ValueError("The object format is not recognized")
    return value