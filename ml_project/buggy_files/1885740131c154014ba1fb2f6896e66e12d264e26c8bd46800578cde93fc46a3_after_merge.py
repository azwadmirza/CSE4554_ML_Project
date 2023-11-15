def default_size_estimator(ctx, chunk, multiplier=1):
    exec_size = int(sum(ctx[inp.key][0] for inp in chunk.inputs or ()) * multiplier)

    total_out_size = 0
    chunk_sizes = dict()
    outputs = chunk.op.outputs
    for out in outputs:
        try:
            chunk_size = out.nbytes if not out.is_sparse() else exec_size
            if np.isnan(chunk_size):
                raise TypeError
            chunk_sizes[out.key] = chunk_size
            total_out_size += chunk_size
        except (AttributeError, TypeError, ValueError):
            pass
    exec_size = max(exec_size, total_out_size)
    for out in outputs:
        if out.key in ctx:
            continue
        if out.key in chunk_sizes:
            store_size = chunk_sizes[out.key]
        else:
            store_size = max(exec_size // len(outputs),
                             total_out_size // max(len(chunk_sizes), 1))
        try:
            max_sparse_size = out.nbytes + np.dtype(np.int64).itemsize * np.prod(out.shape) * out.ndim
        except TypeError:  # pragma: no cover
            max_sparse_size = np.nan
        if not np.isnan(max_sparse_size):
            store_size = min(store_size, max_sparse_size)
        ctx[out.key] = (store_size, exec_size // len(outputs))