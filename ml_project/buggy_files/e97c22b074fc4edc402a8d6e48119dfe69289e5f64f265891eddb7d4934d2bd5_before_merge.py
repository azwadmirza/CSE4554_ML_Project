    def tile(cls, op):
        inputs = op.inputs
        check_chunks_unknown_shape(inputs, TilesError)
        axis_to_nsplits = defaultdict(list)
        has_dataframe = any(output_type == OutputType.dataframe
                            for output_type in op.output_types)
        for ax in op.axes:
            if has_dataframe and ax == 1:
                # if DataFrame exists, for the columns axis,
                # we only allow 1 chunk to ensure the columns consistent
                axis_to_nsplits[ax].append((inputs[0].shape[ax],))
                continue
            for inp in inputs:
                if ax < inp.ndim:
                    axis_to_nsplits[ax].append(inp.nsplits[ax])
        ax_nsplit = {ax: decide_unify_split(*ns) for ax, ns in axis_to_nsplits.items()}
        inputs = [cls._safe_rechunk(inp, ax_nsplit) for inp in inputs]

        mapper_seeds = [None] * len(op.axes)
        reducer_seeds = [None] * len(op.axes)
        for i, ax in enumerate(op.axes):
            rs = np.random.RandomState(op.seeds[i])
            size = len(ax_nsplit[ax])
            if size > 1:
                mapper_seeds[i] = gen_random_seeds(size, rs)
                reducer_seeds[i] = gen_random_seeds(size, rs)
            else:
                mapper_seeds[i] = reducer_seeds[i] = [op.seeds[i]] * size
        out_chunks = []
        out_nsplits = []
        for output_type, inp, oup in zip(op.output_types, inputs, op.outputs):
            inp_axes = tuple(ax for ax in op.axes if ax < inp.ndim)
            reduce_sizes = tuple(inp.chunk_shape[ax] for ax in inp_axes)
            output_types = [output_type]

            if len(inp_axes) == 0:
                continue

            nsplits = list(inp.nsplits)
            for ax in inp_axes:
                cs = len(nsplits[ax])
                if cs > 1:
                    nsplits[ax] = (np.nan,) * cs
            out_nsplits.append(tuple(nsplits))

            if all(reduce_size == 1 for reduce_size in reduce_sizes):
                # no need to do shuffle
                chunks = []
                for c in inp.chunks:
                    chunk_op = LearnShuffle(axes=inp_axes, seeds=op.seeds[:len(inp_axes)],
                                            output_types=output_types)
                    params = cls._calc_chunk_params(c, inp_axes, inp.chunk_shape,
                                                    oup, output_type, chunk_op, True)
                    out_chunk = chunk_op.new_chunk([c], kws=[params])
                    chunks.append(out_chunk)
                out_chunks.append(chunks)
                continue

            if inp.ndim > 1:
                left_chunk_shape = [s for ax, s in enumerate(inp.chunk_shape) if ax not in inp_axes]
                idx_iter = itertools.product(*[range(s) for s in left_chunk_shape])
            else:
                idx_iter = [()]
            reduce_chunks = []
            out_chunks.append(reduce_chunks)
            for idx in idx_iter:
                map_chunks = []
                for reducer_inds in itertools.product(*[range(s) for s in reduce_sizes]):
                    inp_index = list(idx)
                    for ax, reducer_ind in zip(inp_axes, reducer_inds):
                        inp_index.insert(ax, reducer_ind)
                    inp_index = tuple(inp_index)
                    in_chunk = inp.cix[inp_index]
                    params = in_chunk.params
                    map_chunk_op = LearnShuffle(
                        stage=OperandStage.map,
                        output_types=output_types, axes=inp_axes,
                        seeds=tuple(mapper_seeds[j][in_chunk.index[ax]]
                                    for j, ax in enumerate(inp_axes)),
                        reduce_sizes=reduce_sizes
                    )
                    map_chunk = map_chunk_op.new_chunk([in_chunk], **params)
                    map_chunks.append(map_chunk)

                proxy_chunk = LearnShuffleProxy(_tensor_keys=[inp.key]).new_chunk(map_chunks)

                reduce_axes = tuple(ax for j, ax in enumerate(inp_axes) if reduce_sizes[j] > 1)
                reduce_sizes_ = tuple(rs for rs in reduce_sizes if rs > 1)
                for c in map_chunks:
                    shuffle_key = ','.join(str(idx) for idx in c.index)
                    chunk_op = LearnShuffle(
                        stage=OperandStage.reduce,
                        output_types=output_types, axes=reduce_axes,
                        seeds=tuple(reducer_seeds[j][c.index[ax]] for j, ax in enumerate(inp_axes)
                                    if reduce_sizes[j] > 1),
                        reduce_sizes=reduce_sizes_,
                        shuffle_key=shuffle_key)
                    params = cls._calc_chunk_params(c, inp_axes, inp.chunk_shape, oup,
                                                    output_type, chunk_op, False)
                    reduce_chunk = chunk_op.new_chunk([proxy_chunk], kws=[params])
                    reduce_chunks.append(reduce_chunk)

        new_op = op.copy()
        params = [out.params for out in op.outputs]
        if len(out_chunks) < len(op.outputs):
            # axes are all higher than its ndim
            for i, inp in enumerate(op.inputs):
                if all(ax >= inp.ndim for ax in op.axes):
                    out_chunks.insert(i, inp.chunks)
                    out_nsplits.insert(i, inp.nsplits)
            assert len(out_chunks) == len(op.outputs)
        for i, param, chunks, ns in zip(itertools.count(), params, out_chunks, out_nsplits):
            param['chunks'] = chunks
            param['nsplits'] = ns
            param['_position_'] = i
        return new_op.new_tileables(op.inputs, kws=params)