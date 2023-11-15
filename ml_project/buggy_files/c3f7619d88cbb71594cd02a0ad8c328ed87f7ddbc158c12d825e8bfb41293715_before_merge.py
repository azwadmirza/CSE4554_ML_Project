    def submit_to_worker(self, worker, data_metas):
        # worker assigned, submit job
        if self.state in (OperandState.CANCELLED, OperandState.CANCELLING):
            self.start_operand()
            return
        if self.state == OperandState.RUNNING:
            # already running
            return

        self.worker = worker

        target_predicts = self._get_target_predicts(worker)
        try:
            input_metas = self._io_meta['input_data_metas']
            input_chunks = [k[0] if isinstance(k, tuple) else k for k in input_metas]
        except KeyError:
            input_chunks = self._input_chunks

        # submit job
        if set(input_chunks) != set(self._input_chunks) or self._executable_dag is None:
            exec_graph = self._graph_refs[0].get_executable_operand_dag(self._op_key, input_chunks)
        else:
            exec_graph = self._executable_dag
        self._execution_ref = self._get_execution_ref()
        try:
            with rewrite_worker_errors():
                self._submit_promise = self._execution_ref.execute_graph(
                    self._session_id, self._op_key, exec_graph, self._io_meta, data_metas,
                    calc_device=self._calc_device, send_addresses=target_predicts, _promise=True, _spawn=False)
        except WorkerDead:
            logger.debug('Worker %s dead when submitting operand %s into queue',
                         worker, self._op_key)
            self._resource_ref.detach_dead_workers([worker], _tell=True)
        else:
            self.start_operand(OperandState.RUNNING)