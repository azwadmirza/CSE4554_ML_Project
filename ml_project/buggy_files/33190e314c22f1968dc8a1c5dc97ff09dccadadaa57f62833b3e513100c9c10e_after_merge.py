    def _execute_one_chunk(cls, ctx, op):
        (inp,), device_id, xp = as_same_device(
            [ctx[c.key] for c in op.inputs], device=op.device, ret_extra=True)

        with device(device_id):
            inp = inp.astype(np.float32, copy=False)
            # create index
            index = faiss.index_factory(inp.shape[1], op.faiss_index,
                                        op.faiss_metric_type)
            # GPU
            if device_id >= 0:  # pragma: no cover
                index = _index_to_gpu(index, device_id)

            # train index
            if not index.is_trained:
                assert op.n_sample is not None
                sample_indices = xp.random.choice(inp.shape[0],
                                                  size=op.n_sample, replace=False)
                sampled = inp[sample_indices]
                index.train(sampled)

            if op.metric == 'cosine':
                # faiss does not support cosine distances directly,
                # data needs to be normalize before adding to index,
                # refer to:
                # https://github.com/facebookresearch/faiss/wiki/FAQ#how-can-i-index-vectors-for-cosine-distance
                faiss.normalize_L2(inp)
            # add vectors to index
            if device_id >= 0:  # pragma: no cover
                # gpu
                index.add_c(inp.shape[0], _swig_ptr_from_cupy_float32_array(inp))
            else:
                index.add(inp)

            ctx[op.outputs[0].key] = _store_index(ctx, op, index, device_id)