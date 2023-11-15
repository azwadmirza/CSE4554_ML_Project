    def _tile_via_shuffle(cls, op):
        # rechunk the axes except the axis to do unique into 1 chunk
        inp = op.inputs[0]
        if inp.ndim > 1:
            new_chunk_size = dict()
            for axis in range(inp.ndim):
                if axis == op.axis:
                    continue
                if np.isnan(inp.shape[axis]):
                    raise TilesError('input tensor has unknown shape '
                                     'on axis {}'.format(axis))
                new_chunk_size[axis] = inp.shape[axis]
            check_chunks_unknown_shape([inp], TilesError)
            inp = inp.rechunk(new_chunk_size)._inplace_tile()

        aggregate_size = op.aggregate_size
        if aggregate_size is None:
            aggregate_size = max(inp.chunk_shape[op.axis] // options.combine_size, 1)

        unique_on_chunk_sizes = inp.nsplits[op.axis]
        start_poses = np.cumsum((0,) + unique_on_chunk_sizes).tolist()[:-1]
        map_chunks = []
        for c in inp.chunks:
            map_op = TensorUnique(stage=OperandStage.map,
                                  return_index=op.return_index,
                                  return_inverse=op.return_inverse,
                                  return_counts=op.return_counts,
                                  axis=op.axis, aggregate_size=aggregate_size,
                                  start_pos=start_poses[c.index[op.axis]],
                                  dtype=inp.dtype)
            shape = list(c.shape)
            shape[op.axis] = np.nan
            map_chunks.append(map_op.new_chunk([c], shape=tuple(shape), index=c.index))

        shuffle_chunk = TensorShuffleProxy(dtype=inp.dtype, _tensor_keys=[inp.op.key]) \
            .new_chunk(map_chunks, shape=())

        reduce_chunks = [list() for _ in range(len(op.outputs))]
        for i in range(aggregate_size):
            reduce_op = TensorUnique(stage=OperandStage.reduce,
                                     return_index=op.return_index,
                                     return_inverse=op.return_inverse,
                                     return_counts=op.return_counts,
                                     axis=op.axis, aggregate_id=i,
                                     shuffle_key=str(i))
            kws = cls._gen_kws(op, inp, chunk=True, chunk_index=i)
            chunks = reduce_op.new_chunks([shuffle_chunk], kws=kws,
                                          order=op.outputs[0].order)
            for j, c in enumerate(chunks):
                reduce_chunks[j].append(c)

        if op.return_inverse:
            inverse_pos = 2 if op.return_index else 1
            map_inverse_chunks = reduce_chunks[inverse_pos]
            inverse_shuffle_chunk = TensorShuffleProxy(
                dtype=map_inverse_chunks[0].dtype).new_chunk(map_inverse_chunks, shape=())
            inverse_chunks = []
            for j, cs in enumerate(unique_on_chunk_sizes):
                chunk_op = TensorUniqueInverseReduce(dtype=map_inverse_chunks[0].dtype,
                                                     shuffle_key=str(j))
                inverse_chunk = chunk_op.new_chunk([inverse_shuffle_chunk], shape=(cs,),
                                                   index=(j,))
                inverse_chunks.append(inverse_chunk)
            reduce_chunks[inverse_pos] = inverse_chunks

        kws = [out.params for out in op.outputs]
        for kw, chunks in zip(kws, reduce_chunks):
            kw['chunks'] = chunks
        unique_nsplits = list(inp.nsplits)
        unique_nsplits[op.axis] = (np.nan,) * len(reduce_chunks[0])
        kws[0]['nsplits'] = tuple(unique_nsplits)
        i = 1
        if op.return_index:
            kws[i]['nsplits'] = ((np.nan,) * len(reduce_chunks[i]),)
            i += 1
        if op.return_inverse:
            kws[i]['nsplits'] = (inp.nsplits[op.axis],)
            i += 1
        if op.return_counts:
            kws[i]['nsplits'] = ((np.nan,) * len(reduce_chunks[i]),)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, kws=kws)