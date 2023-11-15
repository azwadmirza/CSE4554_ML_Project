    def tile(cls, op):
        q, r = op.outputs
        q_dtype, r_dtype = q.dtype, r.dtype
        q_shape, r_shape = q.shape, r.shape
        in_tensor = op.input
        if in_tensor.chunk_shape == (1, 1):
            in_chunk = in_tensor.chunks[0]
            chunk_op = op.copy().reset_key()
            qr_chunks = chunk_op.new_chunks([in_chunk], (q_shape, r_shape), index=in_chunk.index,
                                            kws=[{'side': 'q'}, {'side': 'r'}])
            q_chunk, r_chunk = qr_chunks

            new_op = op.copy()
            kws = [
                {'chunks': [q_chunk], 'nsplits': ((1,), (1,)), 'dtype': q_dtype},
                {'chunks': [r_chunk], 'nsplits': ((1,), (1,)), 'dtype': r_dtype}
            ]
            return new_op.new_tensors(op.inputs, [q_shape, r_shape], kws=kws)
        elif op.method == 'tsqr':
            return super(TensorQR, cls).tile(op)
        # TODO(hks): support sfqr(short-and-fat qr)
        else:
            raise NotImplementedError('Only tsqr method supported for now')