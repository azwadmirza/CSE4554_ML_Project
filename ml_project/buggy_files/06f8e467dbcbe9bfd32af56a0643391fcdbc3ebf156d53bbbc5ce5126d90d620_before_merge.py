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