def _determine_zarr_chunks(enc_chunks, var_chunks, ndim):
    """
    Given encoding chunks (possibly None) and variable chunks (possibly None)
    """

    # zarr chunk spec:
    # chunks : int or tuple of ints, optional
    #   Chunk shape. If not provided, will be guessed from shape and dtype.

    # if there are no chunks in encoding and the variable data is a numpy
    # array, then we let zarr use its own heuristics to pick the chunks
    if var_chunks is None and enc_chunks is None:
        return None

    # if there are no chunks in encoding but there are dask chunks, we try to
    # use the same chunks in zarr
    # However, zarr chunks needs to be uniform for each array
    # http://zarr.readthedocs.io/en/latest/spec/v1.html#chunks
    # while dask chunks can be variable sized
    # http://dask.pydata.org/en/latest/array-design.html#chunks
    if var_chunks and enc_chunks is None:
        if any(len(set(chunks[:-1])) > 1 for chunks in var_chunks):
            raise ValueError(
                "Zarr requires uniform chunk sizes excpet for final chunk."
                " Variable %r has incompatible chunks. Consider "
                "rechunking using `chunk()`." % (var_chunks,))
        if any((chunks[0] < chunks[-1]) for chunks in var_chunks):
            raise ValueError(
                "Final chunk of Zarr array must be smaller than first. "
                "Variable %r has incompatible chunks. Consider rechunking "
                "using `chunk()`." % var_chunks)
        # return the first chunk for each dimension
        return tuple(chunk[0] for chunk in var_chunks)

    # from here on, we are dealing with user-specified chunks in encoding
    # zarr allows chunks to be an integer, in which case it uses the same chunk
    # size on each dimension.
    # Here we re-implement this expansion ourselves. That makes the logic of
    # checking chunk compatibility easier

    if isinstance(enc_chunks, integer_types):
        enc_chunks_tuple = ndim * (enc_chunks,)
    else:
        enc_chunks_tuple = tuple(enc_chunks)

    if len(enc_chunks_tuple) != ndim:
        raise ValueError("zarr chunks tuple %r must have same length as "
                         "variable.ndim %g" %
                         (enc_chunks_tuple, ndim))

    for x in enc_chunks_tuple:
        if not isinstance(x, int):
            raise TypeError("zarr chunks must be an int or a tuple of ints. "
                            "Instead found %r" % (enc_chunks_tuple,))

    # if there are chunks in encoding and the variable data is a numpy array,
    # we use the specified chunks
    if var_chunks is None:
        return enc_chunks_tuple

    # the hard case
    # DESIGN CHOICE: do not allow multiple dask chunks on a single zarr chunk
    # this avoids the need to get involved in zarr synchronization / locking
    # From zarr docs:
    #  "If each worker in a parallel computation is writing to a separate
    #   region of the array, and if region boundaries are perfectly aligned
    #   with chunk boundaries, then no synchronization is required."
    # TODO: incorporate synchronizer to allow writes from multiple dask
    # threads
    if var_chunks and enc_chunks_tuple:
        for zchunk, dchunks in zip(enc_chunks_tuple, var_chunks):
            for dchunk in dchunks:
                if dchunk % zchunk:
                    raise NotImplementedError(
                        "Specified zarr chunks %r would overlap multiple dask "
                        "chunks %r. This is not implemented in xarray yet. "
                        " Consider rechunking the data using "
                        "`chunk()` or specifying different chunks in encoding."
                        % (enc_chunks_tuple, var_chunks))
        return enc_chunks_tuple

    raise AssertionError(
        "We should never get here. Function logic must be wrong.")