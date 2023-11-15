    def estimate_size(cls, ctx, op):
        from .dataframe.core import DATAFRAME_CHUNK_TYPE, SERIES_CHUNK_TYPE, INDEX_CHUNK_TYPE

        exec_size = 0
        outputs = op.outputs
        if all(not c.is_sparse() and hasattr(c, 'nbytes') and not np.isnan(c.nbytes) for c in outputs):
            for out in outputs:
                ctx[out.key] = (out.nbytes, out.nbytes)

        for inp in op.inputs or ():
            try:
                # execution size of a specific data chunk may be
                # larger than stored type due to objects
                obj_overhead = n_strings = 0
                if getattr(inp, 'shape', None) and not np.isnan(inp.shape[0]):
                    if isinstance(inp, DATAFRAME_CHUNK_TYPE) and inp.dtypes is not None:
                        n_strings = len([dt for dt in inp.dtypes if is_object_dtype(dt)])
                    elif isinstance(inp, (INDEX_CHUNK_TYPE, SERIES_CHUNK_TYPE)) and inp.dtype is not None:
                        n_strings = 1 if is_object_dtype(inp.dtype) else 0
                    obj_overhead += n_strings * inp.shape[0] * OBJECT_FIELD_OVERHEAD

                exec_size += ctx[inp.key][0] + obj_overhead
            except KeyError:
                if not op.sparse:
                    inp_size = calc_data_size(inp)
                    if not np.isnan(inp_size):
                        exec_size += inp_size
        exec_size = int(exec_size)

        total_out_size = 0
        chunk_sizes = dict()
        for out in outputs:
            try:
                chunk_size = calc_data_size(out) if not out.is_sparse() else exec_size
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
                if out.is_sparse():
                    max_sparse_size = out.nbytes + np.dtype(np.int64).itemsize * np.prod(out.shape) * out.ndim
                else:
                    max_sparse_size = np.nan
            except TypeError:  # pragma: no cover
                max_sparse_size = np.nan
            if not np.isnan(max_sparse_size):
                store_size = min(store_size, max_sparse_size)
            ctx[out.key] = (store_size, exec_size // len(outputs))