        def _apply_fail(*exc_info):
            if issubclass(exc_info[0], DependencyMissing):
                logger.warning('DependencyMissing met, operand %s will be back to UNSCHEDULED.',
                               self._op_key)
                self.worker = None
                self.ref().start_operand(OperandState.UNSCHEDULED, _tell=True)
            else:
                raise exc_info[1].with_traceback(exc_info[2]) from None