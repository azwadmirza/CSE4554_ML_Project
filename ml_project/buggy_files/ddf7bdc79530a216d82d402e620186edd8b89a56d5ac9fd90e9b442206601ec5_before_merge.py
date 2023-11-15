def is_pyramid(data):
    """If data is a list of arrays of decreasing size.
    """
    if isinstance(data, list):
        size = [np.prod(d.shape) for d in data]
        return np.all(size[:-1] > size[1:])
    else:
        return False