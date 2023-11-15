    def _on_finished(self):
        if self._last_state == OperandState.CANCELLING:
            self.start_operand(OperandState.CANCELLING)
            return

        futures = []
        # update pred & succ finish records to trigger further actions
        # record if successors can be executed
        for out_key in self._succ_keys:
            futures.append(self._get_operand_actor(out_key).add_finished_predecessor(
                self._op_key, self.worker, _tell=True, _wait=False))
        for in_key in self._pred_keys:
            futures.append(self._get_operand_actor(in_key).add_finished_successor(
                self._op_key, _tell=True, _wait=False))
        # require more chunks to execute if the completion caused no successors to run
        if self._position == OperandPosition.TERMINAL:
            # update records in GraphActor to help decide if the whole graph finished execution
            futures.append(self._graph_ref.add_finished_terminal(
                self._op_key, _tell=True, _wait=False))
        [f.result() for f in futures]