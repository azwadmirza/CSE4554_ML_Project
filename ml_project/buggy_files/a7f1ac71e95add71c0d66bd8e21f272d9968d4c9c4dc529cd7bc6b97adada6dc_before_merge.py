    def _on_cancelled(self):
        futures = []
        if self._position == OperandPosition.TERMINAL:
            futures.append(self._graph_ref.add_finished_terminal(
                self._op_key, final_state=GraphState.CANCELLED, _tell=True, _wait=False))
        for k in self._succ_keys:
            futures.append(self._get_operand_actor(k).stop_operand(
                OperandState.CANCELLING, _tell=True, _wait=False))
        [f.result() for f in futures]