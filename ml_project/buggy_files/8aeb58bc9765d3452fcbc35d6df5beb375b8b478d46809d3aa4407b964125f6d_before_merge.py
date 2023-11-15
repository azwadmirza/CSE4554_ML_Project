def pickle(obj, fname, protocol=2):
    """Pickle object `obj` to file `fname`, using smart_open so that `fname` can be on S3, HDFS, compressed etc.

    Parameters
    ----------
    obj : object
        Any python object.
    fname : str
        Path to pickle file.
    protocol : int, optional
        Pickle protocol number. Default is 2 in order to support compatibility across python 2.x and 3.x.

    """
    with open(fname, 'wb') as fout:  # 'b' for binary, needed on Windows
        _pickle.dump(obj, fout, protocol=protocol)