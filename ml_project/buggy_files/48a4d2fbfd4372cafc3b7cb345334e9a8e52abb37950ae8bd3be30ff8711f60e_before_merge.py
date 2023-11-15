    def _handle_worker_accept(self, worker):
        def _dequeue_worker(endpoint, wait=True):
            try:
                with rewrite_worker_errors():
                    return self._get_execution_ref(address=endpoint).dequeue_graph(
                        self._session_id, self._op_key, _tell=True, _wait=wait)
            finally:
                self._assigned_workers.difference_update((worker,))

        if self._position == OperandPosition.INITIAL:
            new_worker = self._graph_ref.get_operand_target_worker(self._op_key)
            if new_worker and new_worker != self._target_worker:
                logger.debug('Cancelling running operand %s on %s, new_target %s',
                             self._op_key, worker, new_worker)
                _dequeue_worker(worker)
                return

        if (self.worker and self.worker != worker) or \
                (self._target_worker and worker != self._target_worker):
            logger.debug('Cancelling running operand %s on %s, op_worker %s, op_target %s',
                         self._op_key, worker, self.worker, self._target_worker)
            _dequeue_worker(worker)
            return
        elif self.worker is not None:
            logger.debug('Worker for operand %s already assigned', self._op_key)
            return

        # worker assigned, submit job
        if self.state in (OperandState.CANCELLED, OperandState.CANCELLING):
            self.ref().start_operand(_tell=True)
            return

        if worker != self.worker:
            self._execution_ref = None
        self.worker = worker
        cancel_futures = []
        for w in list(self._assigned_workers):
            if w != worker:
                logger.debug('Cancelling running operand %s on %s, when deciding to run on %s',
                             self._op_key, w, worker)
                cancel_futures.append(_dequeue_worker(w, wait=False))

        for f in cancel_futures:
            with rewrite_worker_errors(ignore_error=True):
                f.result()
        self._assigned_workers = set()

        target_predicts = self._get_target_predicts(worker)

        # prepare meta broadcasts
        broadcast_eps = set()
        for succ_key in self._succ_keys:
            broadcast_eps.add(self.get_scheduler(self.gen_uid(self._session_id, succ_key)))
        broadcast_eps.difference_update({self.address})
        broadcast_eps = tuple(broadcast_eps)

        chunk_keys, broadcast_ep_groups = [], []
        for chunk_key in self._chunks:
            chunk_keys.append(chunk_key)
            broadcast_ep_groups.append(broadcast_eps)

        self._chunk_meta_ref.batch_set_chunk_broadcasts(
            self._session_id, chunk_keys, broadcast_ep_groups, _tell=True, _wait=False)

        # submit job
        logger.debug('Start running operand %s on %s', self._op_key, worker)
        self._execution_ref = self._get_execution_ref()
        try:
            with rewrite_worker_errors():
                self._execution_ref.start_execution(
                    self._session_id, self._op_key, send_addresses=target_predicts, _promise=True)
        except WorkerDead:
            self._resource_ref.detach_dead_workers([self.worker], _tell=True)
            return
        # here we start running immediately to avoid accidental state change
        # and potential submission
        self.start_operand(OperandState.RUNNING)