    def _on_fatal(self):
        if self._last_state == OperandState.FATAL:
            return

        futures = []
        if self._position == OperandPosition.TERMINAL:
            # update records in GraphActor to help decide if the whole graph finished execution
            futures.extend(self._add_finished_terminal(final_state=GraphState.FAILED))
        # set successors to FATAL
        for k in self._succ_keys:
            futures.append(self._get_operand_actor(k).stop_operand(
                OperandState.FATAL, _tell=True, _wait=False))
        [f.result() for f in futures]