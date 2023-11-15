def normalize_index(index):
    """
    Flatten a component index.  If it has length 1, then
    return just the element.  If it has length > 1, then
    return a tuple.
    """
    idx = pyutilib.misc.flatten(index)
    if type(idx) is list:
        if len(idx) == 1:
            idx = idx[0]
        else:
            idx = tuple(idx)
    return idx