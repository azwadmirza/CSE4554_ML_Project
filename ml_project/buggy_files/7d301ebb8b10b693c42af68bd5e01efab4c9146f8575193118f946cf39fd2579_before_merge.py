    def _on_running(self):
        self._execution_ref = self._get_execution_ref()

        # notify successors to propagate priority changes
        for out_key in self._succ_keys:
            self._get_operand_actor(out_key).add_running_predecessor(
                self._op_key, self.worker, _tell=True, _wait=False)

        @log_unhandled
        def _acceptor(data_sizes, data_shapes):
            self._allocated = False
            if not self._is_worker_alive():
                return
            self._resource_ref.deallocate_resource(
                self._session_id, self._op_key, self.worker, _tell=True, _wait=False)

            self._data_sizes = data_sizes
            self._data_shapes = data_shapes
            self._io_meta['data_targets'] = list(data_sizes)
            self.start_operand(OperandState.FINISHED)

        @log_unhandled
        def _rejecter(*exc):
            self._allocated = False
            # handling exception occurrence of operand execution
            exc_type = exc[0]
            self._resource_ref.deallocate_resource(
                self._session_id, self._op_key, self.worker, _tell=True, _wait=False)

            if self.state == OperandState.CANCELLING:
                logger.warning('Execution of operand %s cancelled.', self._op_key)
                self.free_data(OperandState.CANCELLED)
                return

            if issubclass(exc_type, ExecutionInterrupted):
                # job cancelled: switch to cancelled
                logger.warning('Execution of operand %s interrupted.', self._op_key)
                self.free_data(OperandState.CANCELLED)
            elif issubclass(exc_type, DependencyMissing):
                logger.warning('Operand %s moved to UNSCHEDULED because of DependencyMissing.',
                               self._op_key)
                self.ref().start_operand(OperandState.UNSCHEDULED, _tell=True)
            else:
                logger.exception('Attempt %d: Unexpected error %s occurred in executing operand %s in %s',
                                 self.retries + 1, exc_type.__name__, self._op_key, self.worker, exc_info=exc)
                # increase retry times
                self.retries += 1
                if not self._info['retryable'] or self.retries >= options.scheduler.retry_num:
                    # no further trial
                    self.state = OperandState.FATAL
                    self._exc = exc
                else:
                    self.state = OperandState.READY
                self.ref().start_operand(_tell=True)

        try:
            with rewrite_worker_errors():
                if self._submit_promise is None:
                    self._submit_promise = self._execution_ref.add_finish_callback(
                        self._session_id, self._op_key, _promise=True, _spawn=False)
                self._submit_promise.then(_acceptor, _rejecter)
        except WorkerDead:
            logger.debug('Worker %s dead when adding callback for operand %s',
                         self.worker, self._op_key)
            self._resource_ref.detach_dead_workers([self.worker], _tell=True)
        finally:
            self._submit_promise = None