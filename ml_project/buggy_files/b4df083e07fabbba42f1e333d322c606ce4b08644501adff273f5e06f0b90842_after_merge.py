    def estimate_size(cls, ctx, op):
        exec_size = 0
        outputs = op.outputs
        pure_dep_keys = \
            set(inp.key for inp, is_dep in zip(op.inputs or (), op.pure_depends or ()) if is_dep)
        if all(not c.is_sparse() and hasattr(c, 'nbytes') and not np.isnan(c.nbytes) for c in outputs):
            for out in outputs:
                ctx[out.key] = (out.nbytes, out.nbytes)

        all_overhead = 0
        for inp in op.inputs or ():
            if inp.key in pure_dep_keys:
                continue
            try:
                if isinstance(inp.op, FetchShuffle):
                    keys_and_shapes = inp.extra_params.get('_shapes', dict()).items()
                else:
                    keys_and_shapes = [(inp.key, getattr(inp, 'shape', None))]

                # execution size of a specific data chunk may be
                # larger than stored type due to objects
                for key, shape in keys_and_shapes:
                    overhead = calc_object_overhead(inp, shape)
                    all_overhead += overhead
                    exec_size += ctx[key][0] + overhead
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
                if not out.is_sparse():
                    chunk_size = calc_data_size(out) + all_overhead // len(outputs)
                else:
                    chunk_size = exec_size
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