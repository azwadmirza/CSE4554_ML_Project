    def tile(cls, op: "LGBMTrain"):
        ctx = get_context()
        if ctx.running_mode != RunningMode.distributed:
            assert all(len(inp.chunks) == 1 for inp in op.inputs)

            chunk_op = op.copy().reset_key()
            out_chunk = chunk_op.new_chunk([inp.chunks[0] for inp in op.inputs],
                                           shape=(1,), index=(0,))
            new_op = op.copy()
            return new_op.new_tileables(op.inputs, chunks=[out_chunk], nsplits=((1,),))
        else:
            data = op.data
            worker_to_args = defaultdict(dict)

            workers = cls._get_data_chunks_workers(ctx, data)
            worker_to_endpoint = cls._build_lgbm_endpoints(workers, op.lgbm_port)
            worker_endpoints = list(worker_to_endpoint.values())

            for arg in ['_data', '_label', '_sample_weight', '_init_score']:
                if getattr(op, arg) is not None:
                    for worker, chunk in cls._concat_chunks_by_worker(
                            getattr(op, arg).chunks, workers).items():
                        worker_to_args[worker][arg] = chunk

            if op.eval_datas:
                eval_workers_list = [cls._get_data_chunks_workers(ctx, d) for d in op.eval_datas]
                extra_workers = reduce(operator.or_, (set(w) for w in eval_workers_list)) - set(workers)
                worker_remap = dict(zip(extra_workers, itertools.cycle(workers)))
                if worker_remap:
                    eval_workers_list = [[worker_remap.get(w, w) for w in wl] for wl in eval_workers_list]

                for arg in ['_eval_datas', '_eval_labels', '_eval_sample_weights', '_eval_init_scores']:
                    if getattr(op, arg):
                        for tileable, eval_workers in zip(getattr(op, arg), eval_workers_list):
                            for worker, chunk in cls._concat_chunks_by_worker(
                                    tileable.chunks, eval_workers).items():
                                if arg not in worker_to_args[worker]:
                                    worker_to_args[worker][arg] = []
                                worker_to_args[worker][arg].append(chunk)

            out_chunks = []
            for worker in workers:
                chunk_op = op.copy().reset_key()

                chunk_op._expect_worker = worker
                chunk_op._lgbm_endpoints = worker_endpoints
                chunk_op._lgbm_port = int(worker_to_endpoint[worker].rsplit(':', 1)[-1])

                input_chunks = []
                concat_args = worker_to_args.get(worker, {})
                for arg in ['_data', '_label', '_sample_weight', '_init_score',
                            '_eval_datas', '_eval_labels', '_eval_sample_weights', '_eval_init_scores']:
                    arg_val = getattr(op, arg)
                    if arg_val:
                        arg_chunk = concat_args.get(arg)
                        setattr(chunk_op, arg, arg_chunk)
                        if isinstance(arg_chunk, list):
                            input_chunks.extend(arg_chunk)
                        else:
                            input_chunks.append(arg_chunk)

                data_chunk = concat_args['_data']
                out_chunk = chunk_op.new_chunk(input_chunks, shape=(np.nan,), index=data_chunk.index[:1])
                out_chunks.append(out_chunk)

            new_op = op.copy()
            return new_op.new_tileables(op.inputs, chunks=out_chunks,
                                        nsplits=((np.nan for _ in out_chunks),))