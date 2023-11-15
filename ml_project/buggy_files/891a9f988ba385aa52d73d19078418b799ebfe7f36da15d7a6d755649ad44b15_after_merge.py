    def tile(cls, op):
        tensor = op.outputs[0]
        chunk_size = tensor.extra_params.raw_chunk_size or options.chunk_size
        nsplits = decide_chunk_sizes(tensor.shape, chunk_size, tensor.dtype.itemsize)
        fields = getattr(op, '_input_fields_', [])
        to_one_chunk_fields = set(getattr(op, '_into_one_chunk_fields_', list()))

        new_inputs = []
        changed = False
        for field in fields:
            t = getattr(op, field)
            if not isinstance(t, TENSOR_TYPE):
                continue

            if field not in to_one_chunk_fields:
                t_nsplits = nsplits
            else:
                t_nsplits = t.shape  # into 1 chunk
            rechunked = t.rechunk(t_nsplits)
            if rechunked is not t:
                rechunked._inplace_tile()
                changed = True
                new_inputs.append(rechunked)
            else:
                new_inputs.append(t)
        if changed:
            op.inputs = new_inputs

        idxes = list(itertools.product(*[range(len(s)) for s in nsplits]))
        seeds = gen_random_seeds(len(idxes), op.state)

        out_chunks = []
        for seed, idx, shape in zip(seeds, idxes, itertools.product(*nsplits)):
            inputs = []
            for inp in op.inputs:
                if len(inp.chunks) == 1:
                    inputs.append(inp.chunks[0])
                else:
                    inputs.append(inp.cix[idx])
            try:
                s = len(tuple(op.size))
                size = shape[:s]
            except TypeError:
                if op.size is None:
                    size = None
                else:
                    size = shape[:1]
            except AttributeError:
                size = shape

            chunk_op = op.copy().reset_key()
            chunk_op._seed = int(seed)
            chunk_op._state = None
            chunk_op._size = size
            out_chunk = chunk_op.new_chunk(inputs, shape=shape, index=idx,
                                           order=tensor.order)
            out_chunks.append(out_chunk)

        new_op = op.copy()
        return new_op.new_tensors(op.inputs, tensor.shape, order=tensor.order,
                                  chunks=out_chunks, nsplits=nsplits, **tensor.extra_params)