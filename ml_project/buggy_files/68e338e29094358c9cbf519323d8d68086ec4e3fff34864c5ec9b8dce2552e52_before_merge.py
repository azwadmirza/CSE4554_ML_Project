    def add_finished_predecessor(self, op_key, worker, output_sizes=None, output_shapes=None):
        super().add_finished_predecessor(op_key, worker, output_sizes=output_sizes,
                                         output_shapes=output_shapes)

        from ..chunkmeta import WorkerMeta
        chunk_key = next(iter(output_sizes.keys()))[0]
        self._mapper_op_to_chunk[op_key] = chunk_key
        if op_key not in self._worker_to_mappers[worker]:
            self._worker_to_mappers[worker].add(op_key)
            self.chunk_meta.add_worker(self._session_id, chunk_key, worker, _tell=True)

        shuffle_keys_to_op = self._shuffle_keys_to_op

        if not self._reducer_workers:
            self._reducer_workers = self._graph_refs[0].assign_operand_workers(
                self._succ_keys, input_chunk_metas=self._reducer_to_mapper)
        reducer_workers = self._reducer_workers
        data_to_addresses = dict()

        for (chunk_key, shuffle_key), data_size in output_sizes.items() or ():
            succ_op_key = shuffle_keys_to_op[shuffle_key]
            meta = self._reducer_to_mapper[succ_op_key][op_key] = \
                WorkerMeta(chunk_size=data_size, workers=(worker,),
                           chunk_shape=output_shapes.get((chunk_key, shuffle_key)))
            reducer_worker = reducer_workers.get(succ_op_key)
            if reducer_worker and reducer_worker != worker:
                data_to_addresses[(chunk_key, shuffle_key)] = [reducer_worker]
                meta.workers += (reducer_worker,)

        if data_to_addresses:
            try:
                with rewrite_worker_errors():
                    self._get_raw_execution_ref(address=worker) \
                        .send_data_to_workers(self._session_id, data_to_addresses, _tell=True)
            except WorkerDead:
                self._resource_ref.detach_dead_workers([worker], _tell=True)

        if all(k in self._finish_preds for k in self._pred_keys):
            self._start_successors()