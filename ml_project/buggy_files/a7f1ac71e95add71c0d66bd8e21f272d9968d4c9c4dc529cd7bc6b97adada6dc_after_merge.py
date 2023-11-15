    def _on_cancelled(self):
        futures = []
        if self._position == OperandPosition.TERMINAL:
            futures.extend(self._add_finished_terminal(final_state=GraphState.CANCELLED))
        for k in self._succ_keys:
            futures.append(self._get_operand_actor(k).stop_operand(
                OperandState.CANCELLING, _tell=True, _wait=False))
        [f.result() for f in futures]