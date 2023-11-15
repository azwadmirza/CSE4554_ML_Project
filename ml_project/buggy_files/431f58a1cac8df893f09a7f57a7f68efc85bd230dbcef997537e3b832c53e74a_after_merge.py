    def _tile_chunks(cls, op, in_tensor, w, v, vi):
        out_tensor = op.outputs[0]
        extra_inputs = []
        for val in [w, v, vi]:
            if val is not None:
                extra_inputs.append(val.chunks[0])

        n = in_tensor.shape[0]
        aggregate_size = op.aggregate_size
        if aggregate_size is None:
            aggregate_size = np.ceil(out_tensor.size * out_tensor.dtype.itemsize /
                                     options.chunk_store_limit).astype(int).item()
        out_sizes = [out_tensor.size // aggregate_size for _ in range(aggregate_size)]
        for i in range(out_tensor.size % aggregate_size):
            out_sizes[i] += 1

        chunk_size = in_tensor.chunk_shape[0]
        map_chunks = []
        axis_0_cum_size = np.cumsum(in_tensor.nsplits[0]).tolist()
        for i in range(chunk_size):
            for j in range(i, chunk_size):
                kw = {
                    'stage': OperandStage.map,
                    'a': in_tensor.cix[i, 0],
                    'a_offset': axis_0_cum_size[i - 1] if i > 0 else 0,
                    'out_sizes': tuple(out_sizes),
                    'n': n,
                    'metric': op.metric,
                    'p': op.p,
                    'w': w.chunks[0] if w is not None else None,
                    'v': v.chunks[0] if v is not None else None,
                    'vi': vi.chunks[0] if vi is not None else None,
                    'dtype': out_tensor.dtype
                }
                if i != j:
                    kw['b'] = in_tensor.cix[j, 0]
                    kw['b_offset'] = axis_0_cum_size[j - 1] if j > 0 else 0
                map_op = TensorPdist(**kw)
                map_chunk_inputs = [kw['a']]
                if 'b' in kw:
                    map_chunk_inputs.append(kw['b'])
                if kw['w'] is not None:
                    map_chunk_inputs.append(kw['w'])
                if kw['v'] is not None:
                    map_chunk_inputs.append(kw['v'])
                if kw['vi'] is not None:
                    map_chunk_inputs.append(kw['vi'])
                # calc chunk shape
                if i == j:
                    a_axis_0_size = kw['a'].shape[0]
                    chunk_shape = (a_axis_0_size * (a_axis_0_size - 1) // 2,)
                else:
                    chunk_shape = (kw['a'].shape[0] * kw['b'].shape[0],)
                map_chunk = map_op.new_chunk(map_chunk_inputs, shape=chunk_shape,
                                             order=out_tensor.order,
                                             index=(i * chunk_size + j,))
                map_chunks.append(map_chunk)

        proxy_chunk = TensorShuffleProxy(dtype=out_tensor.dtype).new_chunk(
            map_chunks, shape=())

        reduce_chunks = []
        for p in range(aggregate_size):
            reduce_chunk_op = TensorPdist(
                stage=OperandStage.reduce, shuffle_key=str(p), dtype=out_tensor.dtype)
            reduce_chunk = reduce_chunk_op.new_chunk(
                [proxy_chunk], shape=(out_sizes[p],), order=out_tensor.order,
                index=(p,))
            reduce_chunks.append(reduce_chunk)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, shape=out_tensor.shape,
                                  order=out_tensor.order,
                                  nsplits=(tuple(out_sizes),),
                                  chunks=reduce_chunks)