def _load_coverage(F, header_length=6,
                   dtype=np.int16):
    """
    load a coverage file.
    This will return a numpy array of the given dtype
    """
    try:
        header = [F.readline() for i in range(header_length)]
    except:
        F = open(F)
        header = [F.readline() for i in range(header_length)]

    make_tuple = lambda t: (t.split()[0], float(t.split()[1]))
    header = dict([make_tuple(line) for line in header])

    M = np.loadtxt(F, dtype=dtype)
    nodata = header['NODATA_value']
    if nodata != -9999:
        M[nodata] = -9999
    return M