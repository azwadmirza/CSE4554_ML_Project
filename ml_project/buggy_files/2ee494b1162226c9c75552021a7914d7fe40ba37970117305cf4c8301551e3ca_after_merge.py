def to_tuple(shape):
    """Convert ints, arrays, and Nones to tuples"""
    if shape is None:
        return tuple()
    temp = np.atleast_1d(shape)
    if temp.size == 0:
        return tuple()
    else:
        return tuple(temp)