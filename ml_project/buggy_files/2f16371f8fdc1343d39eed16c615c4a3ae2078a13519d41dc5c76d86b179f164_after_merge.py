    def tile(cls, op: "ProximaSearcher"):
        tensor = op.tensor
        index = op.index
        topk = op.topk
        outs = op.outputs

        # make sure all inputs have known chunk sizes
        check_chunks_unknown_shape(op.inputs, TilesError)

        if tensor.chunk_shape[1] > 1:
            tensor = tensor.rechunk({1: tensor.shape[1]})._inplace_tile()

        logger.warning(f"query chunks count: {len(tensor.chunks)} ")

        if hasattr(index, 'op'):
            built_indexes = index.chunks
        else:
            # index path
            fs: FileSystem = get_fs(index, op.storage_options)
            built_indexes = [f for f in fs.ls(index)
                             if f.rsplit('/', 1)[-1].startswith('proxima_')]

        if hasattr(index, 'op'):
            ctx = get_context()
            index_chunks_workers = [m.workers[0] if m.workers else None for m in
                                    ctx.get_chunk_metas([c.key for c in index.chunks])]
        else:
            index_chunks_workers = [None] * len(built_indexes)

        out_chunks = [], []
        for tensor_chunk in tensor.chunks:
            pk_chunks, distance_chunks = [], []
            for j, chunk_index, worker in \
                    zip(itertools.count(), built_indexes, index_chunks_workers):
                chunk_op = op.copy().reset_key()
                chunk_op._stage = OperandStage.map
                if hasattr(chunk_index, 'op'):
                    chunk_op._expect_worker = worker
                chunk_op._index = chunk_index
                chunk_kws = [
                    {'index': (tensor_chunk.index[0], j),
                     'dtype': outs[0].dtype,
                     'shape': (tensor_chunk.shape[0], topk),
                     'order': TensorOrder.C_ORDER},
                    {'index': (tensor_chunk.index[0], j),
                     'dtype': outs[1].dtype,
                     'shape': (tensor_chunk.shape[0], topk),
                     'order': TensorOrder.C_ORDER}
                ]
                chunk_inputs = [tensor_chunk]
                if hasattr(chunk_index, 'op'):
                    chunk_inputs.append(chunk_index)
                pk_chunk, distance_chunk = chunk_op.new_chunks(
                    chunk_inputs, kws=chunk_kws)
                pk_chunks.append(pk_chunk)
                distance_chunks.append(distance_chunk)

            if len(pk_chunks) == 1:
                out_chunks[0].append(pk_chunks[0])
                out_chunks[1].append(distance_chunks[0])
                continue

            shape = (tensor_chunk.shape[0], topk * len(pk_chunks))
            pk_merge_op = TensorConcatenate(axis=1)
            pk_merge_chunk = pk_merge_op.new_chunk(
                pk_chunks, index=(pk_chunks[0].index[0], 0), shape=shape,
                dtype=pk_chunks[0].dtype, order=pk_chunks[0].order)
            distance_merge_op = TensorConcatenate(axis=1)
            distance_merge_chunk = distance_merge_op.new_chunk(
                distance_chunks, index=(distance_chunks[0].index[0], 0), shape=shape,
                dtype=distance_chunks[0].dtype, order=distance_chunks[0].order)

            agg_op = ProximaSearcher(stage=OperandStage.agg,
                                     topk=op.topk,
                                     distance_metric=op.distance_metric)
            agg_chunk_kws = [
                {'index': pk_merge_chunk.index,
                 'dtype': outs[0].dtype,
                 'shape': (tensor_chunk.shape[0], topk),
                 'order': outs[0].order},
                {'index': pk_merge_chunk.index,
                 'dtype': outs[1].dtype,
                 'shape': (tensor_chunk.shape[0], topk),
                 'order': outs[1].order}
            ]
            pk_result_chunk, distance_result_chunk = agg_op.new_chunks(
                [pk_merge_chunk, distance_merge_chunk],
                kws=agg_chunk_kws)
            out_chunks[0].append(pk_result_chunk)
            out_chunks[1].append(distance_result_chunk)

        logger.warning(f"query out_chunks count: {len(out_chunks)} ")

        kws = []
        pk_params = outs[0].params
        pk_params['chunks'] = out_chunks[0]
        pk_params['nsplits'] = (tensor.nsplits[0], (topk,))
        kws.append(pk_params)
        distance_params = outs[1].params
        distance_params['chunks'] = out_chunks[1]
        distance_params['nsplits'] = (tensor.nsplits[0], (topk,))
        kws.append(distance_params)
        new_op = op.copy()
        return new_op.new_tileables(op.inputs, kws=kws)