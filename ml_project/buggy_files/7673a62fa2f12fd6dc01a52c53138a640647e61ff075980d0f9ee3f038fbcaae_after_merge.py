def _chk_asarray(a, axis):
    if len(np.array(a).shape) == 0:
        a = np.atleast_1d(a)

    if axis is None:
        a = np.ravel(a)
        outaxis = 0
    else:
        a = np.asarray(a)
        outaxis = axis
    return a, outaxis