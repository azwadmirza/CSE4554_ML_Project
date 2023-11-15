    def tile(cls, op):
        get_obj_attr = cls._get_obj_attr
        U, s, V = op.outputs
        U_dtype, s_dtype, V_dtype = \
            get_obj_attr(U, 'dtype'), get_obj_attr(s, 'dtype'), get_obj_attr(V, 'dtype')
        U_shape, s_shape, V_shape = \
            get_obj_attr(U, 'shape'), get_obj_attr(s, 'shape'), get_obj_attr(V, 'shape')
        in_tensor = op.input
        if in_tensor.chunk_shape == (1, 1):
            in_chunk = in_tensor.chunks[0]
            chunk_op = op.copy().reset_key()
            svd_chunks = chunk_op.new_chunks([in_chunk], (U_shape, s_shape, V_shape),
                                             kws=[
                                                 {'side': 'U', 'dtype': U_dtype,
                                                  'index': in_chunk.index},
                                                 {'side': 's', 'dtype': s_dtype,
                                                  'index': in_chunk.index[1:]},
                                                 {'side': 'V', 'dtype': V_dtype,
                                                  'index': in_chunk.index}
                                             ])
            U_chunk, s_chunk, V_chunk = svd_chunks

            new_op = op.copy()
            kws = [
                {'chunks': [U_chunk], 'nsplits': tuple((s,) for s in U_shape), 'dtype': U_dtype},
                {'chunks': [s_chunk], 'nsplits': tuple((s,) for s in s_shape), 'dtype': s_dtype},
                {'chunks': [V_chunk], 'nsplits': tuple((s,) for s in V_shape), 'dtype': V_dtype}
            ]
            return new_op.new_tensors(op.inputs, [U_shape, s_shape, V_shape], kws=kws)
        elif op.method == 'tsqr':
            return super(TensorSVD, cls).tile(op)
        else:
            raise NotImplementedError('Only tsqr method supported for now')