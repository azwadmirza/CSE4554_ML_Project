    def _on_fatal(self):
        if self._last_state == OperandState.FATAL:
            return

        futures = []
        if self._position == OperandPosition.TERMINAL:
            # update records in GraphActor to help decide if the whole graph finished execution
            futures.append(self._graph_ref.add_finished_terminal(
                self._op_key, final_state=GraphState.FAILED, _tell=True, _wait=False))
        # set successors to FATAL
        for k in self._succ_keys:
            futures.append(self._get_operand_actor(k).stop_operand(
                OperandState.FATAL, _tell=True, _wait=False))
        [f.result() for f in futures]