def _chk2_asarray(a, b, axis):
    if len(np.array(a).shape) == 0:
        a = np.atleast_1d(a)
    if len(np.array(b).shape) == 0:
        b = np.atleast_1d(b)

    if axis is None:
        a = np.ravel(a)
        b = np.ravel(b)
        outaxis = 0
    else:
        a = np.asarray(a)
        b = np.asarray(b)
        outaxis = axis
    return a, b, outaxis