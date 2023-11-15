def _load_csv(F):
    """Load csv file.

    Parameters
    ----------
    F : file object
        CSV file open in byte mode.
    Returns
    -------
    rec : np.ndarray
        record array representing the data
    """
    if PY2:
        # Numpy recarray wants Python 2 str but not unicode
        names = F.readline().strip().split(',')
    else:
        # Numpy recarray wants Python 3 str but not bytes...
        names = F.readline().decode('ascii').strip().split(',')
    rec = np.loadtxt(F, skiprows=0, delimiter=',', dtype='a22,f4,f4')
    rec.dtype.names = names
    return rec