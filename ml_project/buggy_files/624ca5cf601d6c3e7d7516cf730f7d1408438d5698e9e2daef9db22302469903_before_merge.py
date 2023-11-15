def normalize(data, wrt):
    """ Normalize data to be in range (0,1), with respect to (wrt) boundaries,
        which can be specified.
    """
    return (data - np.min(wrt, axis=0)) / (
        np.max(wrt, axis=0) - np.min(wrt, axis=0))