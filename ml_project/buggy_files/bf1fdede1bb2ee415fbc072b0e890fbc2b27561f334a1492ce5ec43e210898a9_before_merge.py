def fromtiledb(uri, ctx=None, key=None, timestamp=None, gpu=False):
    import tiledb

    raw_ctx = ctx
    if raw_ctx is None:
        ctx = tiledb.Ctx()

    # get metadata from tiledb
    try:
        tiledb_arr = tiledb.DenseArray(uri=uri, ctx=ctx, key=key, timestamp=timestamp)
        sparse = False
    except ValueError:
        # if the array is not dense, ValueError will be raised by tiledb
        tiledb_arr = tiledb.SparseArray(uri=uri, ctx=ctx, key=key, timestamp=timestamp)
        sparse = True

    if tiledb_arr.nattr > 1:
        raise NotImplementedError('Does not supported TileDB array schema '
                                  'with more than 1 attr')
    tiledb_dim_starts = tuple(tiledb_arr.domain.dim(j).domain[0]
                              for j in range(tiledb_arr.ndim))
    if any(isinstance(s, float) for s in tiledb_dim_starts):
        raise ValueError('Does not support TileDB array schema '
                         'whose dimensions has float domain')

    dtype = tiledb_arr.attr(0).dtype
    tiledb_config = None if raw_ctx is None else ctx.config().dict()
    tensor_order = TensorOrder.C_ORDER \
        if tiledb_arr.schema.cell_order == 'row-major' else TensorOrder.F_ORDER
    op = TensorTileDBDataSource(tiledb_config=tiledb_config, tiledb_uri=uri,
                                tiledb_key=key, tiledb_timstamp=timestamp,
                                tiledb_dim_starts=tiledb_dim_starts,
                                gpu=gpu, sparse=sparse, dtype=dtype)
    chunk_size = tuple(int(tiledb_arr.domain.dim(i).tile)
                       for i in range(tiledb_arr.domain.ndim))
    return op(tiledb_arr.shape, chunk_size=chunk_size, order=tensor_order)