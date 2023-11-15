    def add_running_predecessor(self, op_key, worker):
        self._running_preds.add(op_key)
        self._pred_workers.add(worker)
        if len(self._pred_workers) > 1:
            # we do not push when multiple workers in input
            self._pred_workers = set()
            self._running_preds = set()
            return

        if self.state != OperandState.UNSCHEDULED:
            return

        if all(k in self._running_preds for k in self._pred_keys):
            try:
                if worker in self._assigned_workers:
                    return
                serialized_exec_graph = self._graph_refs[0].get_executable_operand_dag(self._op_key)

                self._get_execution_ref(address=worker).enqueue_graph(
                    self._session_id, self._op_key, serialized_exec_graph, self._io_meta,
                    dict(), self._info['optimize'], succ_keys=self._succ_keys,
                    pred_keys=self._pred_keys, _promise=True) \
                    .then(functools.partial(self._handle_worker_accept, worker))
                self._assigned_workers.add(worker)
                logger.debug('Pre-push operand %s into worker %s.', self._op_key, worker)
            except:  # noqa: E722
                logger.exception('Failed to pre-push operand %s', self._op_key)
            finally:
                self._pred_workers = set()
                self._running_preds = set()