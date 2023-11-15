    def _on_ready(self):
        self.worker = None
        self._execution_ref = None

        def _apply_fail(*exc_info):
            if issubclass(exc_info[0], DependencyMissing):
                logger.warning('DependencyMissing met, operand %s will be back to UNSCHEDULED.',
                               self._op_key)
                self.worker = None
                self.ref().start_operand(OperandState.UNSCHEDULED, _tell=True)
            else:
                self.handle_unexpected_failure(*exc_info)

        # if under retry, give application a delay
        delay = options.scheduler.retry_delay if self.retries else 0
        # Send resource application. Submit job when worker assigned
        if not self._allocated:
            self._assigner_ref.apply_for_resource(
                self._session_id, self._op_key, self._info, _delay=delay, _promise=True) \
                .catch(_apply_fail)