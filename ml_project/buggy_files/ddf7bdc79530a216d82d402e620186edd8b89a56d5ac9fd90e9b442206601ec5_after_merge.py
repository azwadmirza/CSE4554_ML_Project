def is_pyramid(data):
    """If shape of arrays along first axis is strictly decreasing.
    """
    size = np.array([np.prod(d.shape) for d in data])
    if len(size) > 1:
        return np.all(size[:-1] > size[1:])
    else:
        return False