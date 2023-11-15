    def tile(cls, op):
        from ..merge.concatenate import TensorConcatenate
        from ..indexing.slice import TensorSlice
        from .dot import TensorDot
        from .qr import TensorQR
        from .svd import TensorSVD

        calc_svd = getattr(op, '_is_svd', lambda: None)() or False

        a = op.input

        tinyq, tinyr = np.linalg.qr(np.ones((1, 1), dtype=a.dtype))
        q_dtype, r_dtype = tinyq.dtype, tinyr.dtype

        if a.chunk_shape[1] != 1:
            check_chunks_unknown_shape([a], TilesError)
            new_chunk_size = decide_chunk_sizes(a.shape, {1: a.shape[1]}, a.dtype.itemsize)
            a = a.rechunk(new_chunk_size)._inplace_tile()

        # stage 1, map phase
        stage1_q_chunks, stage1_r_chunks = stage1_chunks = [[], []]  # Q and R chunks
        for c in a.chunks:
            x, y = c.shape
            q_shape, r_shape = (c.shape, (y, y)) if x > y else ((x, x), c.shape)
            qr_op = TensorQR()
            qr_chunks = qr_op.new_chunks([c], index=c.index,
                                         kws=[{'side': 'q', 'dtype': q_dtype, 'shape': q_shape},
                                              {'side': 'r', 'dtype': r_dtype, 'shape': r_shape}])
            stage1_chunks[0].append(qr_chunks[0])
            stage1_chunks[1].append(qr_chunks[1])

        # stage 2, reduce phase
        # concatenate all r chunks into one
        shape = (sum(c.shape[0] for c in stage1_r_chunks), stage1_r_chunks[0].shape[1])
        concat_op = TensorConcatenate(axis=0, dtype=stage1_r_chunks[0].dtype)
        concat_r_chunk = concat_op.new_chunk(stage1_r_chunks, shape=shape,
                                             index=(0, 0), order=TensorOrder.C_ORDER)
        qr_op = TensorQR()
        qr_chunks = qr_op.new_chunks([concat_r_chunk], index=concat_r_chunk.index,
                                     kws=[{'side': 'q', 'dtype': q_dtype, 'order': TensorOrder.C_ORDER,
                                           'shape': (concat_r_chunk.shape[0], min(concat_r_chunk.shape))},
                                          {'side': 'r', 'dtype': r_dtype, 'order': TensorOrder.C_ORDER,
                                           'shape': (min(concat_r_chunk.shape), concat_r_chunk.shape[1])}])
        stage2_q_chunk, stage2_r_chunk = qr_chunks

        # stage 3, map phase
        # split stage2_q_chunk into the same size as stage1_q_chunks
        q_splits = np.cumsum([c.shape[1] for c in stage1_q_chunks]).tolist()
        q_slices = [slice(q_splits[i]) if i == 0 else slice(q_splits[i-1], q_splits[i])
                    for i in range(len(q_splits))]
        stage2_q_chunks = []
        for c, s in zip(stage1_q_chunks, q_slices):
            slice_op = TensorSlice(slices=[s], dtype=c.dtype)
            slice_length = s.stop - (s.start or 0)
            stage2_q_chunks.append(slice_op.new_chunk([stage2_q_chunk], index=c.index,
                                                      order=TensorOrder.C_ORDER,
                                                      shape=(slice_length, stage2_q_chunk.shape[1])))
        stage3_q_chunks = []
        for c1, c2 in zip(stage1_q_chunks, stage2_q_chunks):
            dot_op = TensorDot(dtype=q_dtype)
            shape = (c1.shape[0], c2.shape[1])
            stage3_q_chunks.append(dot_op.new_chunk([c1, c2], shape=shape, index=c1.index,
                                                    order=TensorOrder.C_ORDER))

        if not calc_svd:
            q, r = op.outputs
            new_op = op.copy()
            q_nsplits = (tuple(c.shape[0] for c in stage3_q_chunks), (stage3_q_chunks[0].shape[1],))
            r_nsplits = ((stage2_r_chunk.shape[0],), (stage2_r_chunk.shape[1],))
            kws = [
                # Q
                {'chunks': stage3_q_chunks, 'nsplits': q_nsplits, 'dtype': q.dtype, 'shape': q.shape},
                # R, calculate from stage2
                {'chunks': [stage2_r_chunk], 'nsplits': r_nsplits, 'dtype': r.dtype, 'shape': r.shape}
            ]
            return new_op.new_tensors(op.inputs, kws=kws)
        else:
            U, s, V = op.outputs
            U_dtype, s_dtype, V_dtype = U.dtype, s.dtype, V.dtype
            U_shape, s_shape, V_shape = U.shape, s.shape, V.shape

            svd_op = TensorSVD()
            u_shape, s_shape, v_shape = calc_svd_shapes(stage2_r_chunk)
            stage2_usv_chunks = svd_op.new_chunks([stage2_r_chunk],
                                                  kws=[{'side': 'U', 'dtype': U_dtype,
                                                        'index': stage2_r_chunk.index,
                                                        'shape': u_shape,
                                                        'order': TensorOrder.C_ORDER},
                                                       {'side': 's', 'dtype': s_dtype,
                                                        'index': stage2_r_chunk.index[1:],
                                                        'shape': s_shape,
                                                        'order': TensorOrder.C_ORDER},
                                                       {'side': 'V', 'dtype': V_dtype,
                                                        'index': stage2_r_chunk.index,
                                                        'shape': v_shape,
                                                        'order': TensorOrder.C_ORDER}])
            stage2_u_chunk, stage2_s_chunk, stage2_v_chunk = stage2_usv_chunks

            # stage 4, U = Q @ u
            stage4_u_chunks = []
            if U is not None:  # U is not garbage collected
                for c1 in stage3_q_chunks:
                    dot_op = TensorDot(dtype=U_dtype)
                    shape = (c1.shape[0], stage2_u_chunk.shape[1])
                    stage4_u_chunks.append(dot_op.new_chunk([c1, stage2_u_chunk], shape=shape,
                                                            index=c1.index,
                                                            order=TensorOrder.C_ORDER))

            new_op = op.copy()
            u_nsplits = (tuple(c.shape[0] for c in stage4_u_chunks), (stage4_u_chunks[0].shape[1],))
            s_nsplits = ((stage2_s_chunk.shape[0],),)
            v_nsplits = ((stage2_v_chunk.shape[0],), (stage2_v_chunk.shape[1],))
            kws = [
                {'chunks': stage4_u_chunks, 'nsplits': u_nsplits,
                 'dtype': U_dtype, 'shape': U_shape, 'order': U.order},   # U
                {'chunks': [stage2_s_chunk], 'nsplits': s_nsplits,
                 'dtype': s_dtype, 'shape': s_shape, 'order': s.order},  # s
                {'chunks': [stage2_v_chunk], 'nsplits': v_nsplits,
                 'dtype': V_dtype, 'shape': V_shape, 'order': V.order},  # V
            ]
            return new_op.new_tensors(op.inputs, kws=kws)