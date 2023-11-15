    def _on_ready(self):
        self.worker = None
        self._execution_ref = None

        # if under retry, give application a delay
        delay = options.scheduler.retry_delay if self.retries else 0
        # Send resource application. Submit job when worker assigned
        try:
            new_assignment = self._assigner_ref.get_worker_assignments(
                self._session_id, self._info)
        except DependencyMissing:
            logger.warning('DependencyMissing met, operand %s will be back to UNSCHEDULED.',
                           self._op_key)
            self._assigned_workers = set()
            self.ref().start_operand(OperandState.UNSCHEDULED, _tell=True)
            return

        chunk_sizes = self._chunk_meta_ref.batch_get_chunk_size(self._session_id, self._input_chunks)
        if any(v is None for v in chunk_sizes):
            logger.warning('DependencyMissing met, operand %s will be back to UNSCHEDULED.',
                           self._op_key)
            self._assigned_workers = set()
            self.ref().start_operand(OperandState.UNSCHEDULED, _tell=True)
            return

        new_assignment = [a for a in new_assignment if a not in self._assigned_workers]
        self._assigned_workers.update(new_assignment)
        logger.debug('Operand %s assigned to run on workers %r, now it has %r',
                     self._op_key, new_assignment, self._assigned_workers)

        data_sizes = dict(zip(self._input_chunks, chunk_sizes))

        dead_workers = set()
        serialized_exec_graph = self._graph_refs[0].get_executable_operand_dag(self._op_key)
        for worker_ep in new_assignment:
            try:
                with rewrite_worker_errors():
                    self._get_execution_ref(address=worker_ep).enqueue_graph(
                        self._session_id, self._op_key, serialized_exec_graph, self._io_meta,
                        data_sizes, self._info['optimize'], succ_keys=self._succ_keys,
                        _delay=delay, _promise=True) \
                        .then(functools.partial(self._handle_worker_accept, worker_ep))
            except WorkerDead:
                logger.debug('Worker %s dead when submitting operand %s into queue',
                             worker_ep, self._op_key)
                dead_workers.add(worker_ep)
                self._assigned_workers.difference_update([worker_ep])
        if dead_workers:
            self._resource_ref.detach_dead_workers(list(dead_workers), _tell=True)
            if not self._assigned_workers:
                self.ref().start_operand(_tell=True)