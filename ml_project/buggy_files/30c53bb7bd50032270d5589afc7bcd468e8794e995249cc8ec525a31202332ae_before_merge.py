    def _execute_map(cls, ctx, op):
        (data,), device_id, _ = as_same_device(
            [ctx[op.inputs[0].key]], device=op.device, ret_extra=True)
        index = ctx[op.inputs[1].key] if len(op.inputs) == 2 else None

        with device(device_id):
            if index is not None:
                # fetch the trained index
                trained_index = _load_index(ctx, op, index, device_id)
                return_index_type = _get_index_type(op.return_index_type, ctx)
                if return_index_type == 'object':
                    # clone a new one,
                    # because faiss does not ensure thread-safe for operations that change index
                    # https://github.com/facebookresearch/faiss/wiki/Threads-and-asynchronous-calls#thread-safety
                    trained_index = faiss.clone_index(trained_index)
            else:
                trained_index = faiss.index_factory(data.shape[1], op.faiss_index,
                                                    op.faiss_metric_type)
                if op.same_distribution:
                    # no need to train, just create index
                    pass
                else:
                    # distribution no the same, train on each chunk
                    trained_index.train(data)

                if device_id >= 0:  # pragma: no cover
                    trained_index = _index_to_gpu(trained_index, device_id)
            if op.metric == 'cosine':
                # faiss does not support cosine distances directly,
                # data needs to be normalize before adding to index,
                # refer to:
                # https://github.com/facebookresearch/faiss/wiki/FAQ#how-can-i-index-vectors-for-cosine-distance
                faiss.normalize_L2(data)

            # add data into index
            if device_id >= 0:  # pragma: no cover
                # gpu
                trained_index.add_c(data.shape[0], _swig_ptr_from_cupy_float32_array(data))
            else:
                trained_index.add(data)

            ctx[op.outputs[0].key] = _store_index(ctx, op, trained_index, device_id)