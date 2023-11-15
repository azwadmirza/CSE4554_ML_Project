def from_array(array, dtag=None, dcompress=None, chunksize=None) -> Tensor:
    """Generates tensor from arraylike object
    Parameters
    ----------
    array : np.ndarray
        Numpy array like object with shape, dtype, dims
    dtag : str, optional
        Describes type of the data stored in this array (image, mask, labels, ...)
    dcompress: str, optional
        Argument for compression algorithm, ignore this one, this one does not have any affect yet!
    chunksize:
        Information about how many items (from axis 0) should be stored in the same file if a command is given to save this tensor

    Returns
    -------
    Tensor
        newly generated tensor itself
    """
    if "dask" not in sys.modules:
        raise ModuleNotInstalledException("dask")
    else:
        import dask
        import dask.array

        global dask
    meta = {
        "dtype": array.dtype,
        "dtag": dtag,
        "dcompress": dcompress,
        "chunksize": chunksize,
    }
    if str(array.dtype) == "object":
        array = dask.array.from_array(array, chunks=1)
    else:
        array = dask.array.from_array(array)
    return Tensor(meta, array)