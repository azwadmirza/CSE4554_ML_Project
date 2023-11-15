def _good_shape(x, shape, axes):
    """Ensure that shape argument is valid for scipy.fftpack

    scipy.fftpack does not support len(shape) < x.ndim when axes is not given.
    """
    if shape and not axes:
        shape = _helper._iterable_of_int(shape, 'shape')
        if len(shape) != np.ndim(x):
            raise ValueError("when given, axes and shape arguments"
                             " have to be of the same length")
    return shape