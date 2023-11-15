    def tile(cls, op):
        ctx = get_context()
        if ctx.running_mode != RunningMode.distributed:
            assert all(len(inp.chunks) == 1 for inp in op.inputs)

            chunk_op = op.copy().reset_key()
            out_chunk = chunk_op.new_chunk([inp.chunks[0] for inp in op.inputs],
                                           shape=(1,), index=(0,))
            new_op = op.copy()
            return new_op.new_tileables(op.inputs, chunks=[out_chunk], nsplits=((1,),))
        else:
            inp = op.inputs[0]
            in_chunks = inp.chunks
            workers = cls._get_dmatrix_chunks_workers(ctx, inp)
            tracker_chunk = StartTracker(n_workers=len(in_chunks)).new_chunk(in_chunks, shape=())
            out_chunks = []
            worker_to_evals = defaultdict(list)
            if op.evals is not None:
                for dm, ev in op.evals:
                    worker_to_chunk = cls._get_dmatrix_worker_to_chunk(dm, workers, ctx)
                    for worker, chunk in worker_to_chunk.items():
                        worker_to_evals[worker].append((chunk, ev))
            for in_chunk, worker in zip(in_chunks, workers):
                chunk_op = op.copy().reset_key()
                chunk_op._expect_worker = worker
                chunk_op._tracker = tracker_chunk
                chunk_evals = list(worker_to_evals.get(worker, list()))
                chunk_op._evals = chunk_evals
                input_chunks = [in_chunk] + [pair[0] for pair in chunk_evals] + [tracker_chunk]
                out_chunk = chunk_op.new_chunk(input_chunks, shape=(np.nan,),
                                               index=in_chunk.index[:1])
                out_chunks.append(out_chunk)

            new_op = op.copy()
            return new_op.new_tileables(op.inputs, chunks=out_chunks,
                                        nsplits=((np.nan for _ in out_chunks),))