def _load_csv(F):
    """Load csv file.

    Parameters
    ----------
    F : string or file object
        file object or name of file

    Returns
    -------
    rec : np.ndarray
        record array representing the data
    """
    try:
        names = F.readline().strip().split(',')
    except:
        F = open(F)
        names = F.readline().strip().split(',')

    rec = np.loadtxt(F, skiprows=1, delimiter=',',
                     dtype='a22,f4,f4')
    rec.dtype.names = names

    return rec