    def tile(cls, op):
        in_tensor = op.input
        tensor = op.outputs[0]

        # check unknown shape
        check_chunks_unknown_shape(op.inputs, TilesError)

        if any(np.isnan(s) for s in tensor.shape):
            # -1 exists in newshape and input tensor has unknown shape
            # recalculate new shape
            shape = tuple(-1 if np.isnan(s) else s for s in tensor.shape)
            newshape = calc_shape(in_tensor.size, shape)
            tensor._shape = newshape

        if op.order == 'F':
            # do transpose first, then do regular reshape, then transpose back
            result = in_tensor.transpose().reshape(op.newshape[::-1])
            if getattr(op, '_reshape_with_shuffle', True):
                result.op.extra_params['_reshape_with_shuffle'] = True
            result = result.transpose()
            return [recursive_tile(result)]

        if len(in_tensor.chunks) == 1:
            # 1 chunk
            chunk_op = op.copy().reset_key()
            chunk = chunk_op.new_chunk(in_tensor.chunks, shape=tensor.shape,
                                       order=tensor.order, index=(0,) * tensor.ndim)
            new_op = op.copy()
            return new_op.new_tensors(op.inputs, shape=tensor.shape,
                                      order=tensor.order, chunks=[chunk],
                                      nsplits=tuple((s,) for s in tensor.shape))
        try:
            rechunk_nsplits, reshape_nsplits = cls._gen_reshape_rechunk_nsplits(
                in_tensor.shape, tensor.shape, in_tensor.nsplits)
            rechunked_tensor = in_tensor.rechunk(rechunk_nsplits)._inplace_tile()
            in_idxes = itertools.product(*[range(len(s)) for s in rechunk_nsplits])
            out_idxes = itertools.product(*[range(len(s)) for s in reshape_nsplits])
            out_shape = itertools.product(*[s for s in reshape_nsplits])
            out_chunks = []
            for input_idx, out_idx, out_shape in zip(in_idxes, out_idxes, out_shape):
                in_chunk = rechunked_tensor.cix[input_idx]
                chunk_op = op.copy().reset_key()
                chunk_op._newshape = out_shape
                out_chunk = chunk_op.new_chunk([in_chunk], shape=out_shape,
                                               order=tensor.order, index=out_idx)
                out_chunks.append(out_chunk)

            new_op = op.copy()
            return new_op.new_tensors(op.inputs, tensor.shape, order=tensor.order,
                                      chunks=out_chunks, nsplits=reshape_nsplits)
        except ValueError:
            # TODO: make this as default when shuffle is mature
            if getattr(op.extra_params, '_reshape_with_shuffle', False):
                return cls._tile_as_shuffle(op)

            # shape incompatible, we will first do flatten, then reshape to the new shape
            return [in_tensor.reshape(-1, order=tensor.op.order)._inplace_tile().reshape(
                tensor.shape, order=tensor.op.order)._inplace_tile()]