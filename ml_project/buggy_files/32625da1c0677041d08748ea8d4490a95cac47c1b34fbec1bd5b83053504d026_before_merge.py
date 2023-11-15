    def move_failover_state(self, from_states, state, new_target, dead_workers):
        """
        Move the operand into new state when executing fail-over step
        :param from_states: the source states the operand should be in, when not match, we stopped.
        :param state: the target state to move
        :param new_target: new target worker proposed for worker
        :param dead_workers: list of dead workers
        :return:
        """
        dead_workers = set(dead_workers)
        if self.state not in from_states:
            logger.debug('From state not matching (%s not in %r), operand %s skips failover step',
                         self.state.name, [s.name for s in from_states], self._op_key)
            return
        if self.state in (OperandState.RUNNING, OperandState.FINISHED):
            if state != OperandState.UNSCHEDULED and self.worker not in dead_workers:
                logger.debug('Worker %s of operand %s still alive, skip failover step',
                             self.worker, self._op_key)
                return
            elif state == OperandState.RUNNING:
                # move running operand in dead worker to ready
                state = OperandState.READY

        if new_target and self._target_worker != new_target:
            logger.debug('Target worker of %s reassigned to %s', self._op_key, new_target)
            self._target_worker = new_target
            self._info['target_worker'] = new_target
            target_updated = True
        else:
            target_updated = False

        if self.state == state == OperandState.READY:
            if not self._target_worker:
                if self._assigned_workers - dead_workers:
                    logger.debug('Operand %s still have alive workers assigned %r, skip failover step',
                                 self._op_key, list(self._assigned_workers - dead_workers))
                    return
            else:
                if not target_updated and self._target_worker not in dead_workers:
                    logger.debug('Target of operand %s (%s) not dead, skip failover step',
                                 self._op_key, self._target_worker)
                    return

        if dead_workers:
            futures = []
            # remove executed traces in neighbor operands
            for out_key in self._succ_keys:
                futures.append(self._get_operand_actor(out_key).remove_finished_predecessor(
                    self._op_key, _tell=True, _wait=False))
            for in_key in self._pred_keys:
                futures.append(self._get_operand_actor(in_key).remove_finished_successor(
                    self._op_key, _tell=True, _wait=False))
            if self._position == OperandPosition.TERMINAL:
                futures.append(self._graph_ref.remove_finished_terminal(
                    self._op_key, _tell=True, _wait=False))
            [f.result() for f in futures]

        # actual start the new state
        self.start_operand(state)