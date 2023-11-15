def to_tuple(shape):
    """Convert ints, arrays, and Nones to tuples"""
    if shape is None:
        return tuple()
    return tuple(np.atleast_1d(shape))