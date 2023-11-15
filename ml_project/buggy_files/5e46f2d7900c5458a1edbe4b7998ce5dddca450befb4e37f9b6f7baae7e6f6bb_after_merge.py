    def add_finished_successor(self, op_key):
        super(OperandActor, self).add_finished_successor(op_key)
        if self._position != OperandPosition.TERMINAL and \
                all(k in self._finish_succs for k in self._succ_keys):
            # make sure that all prior states are terminated (in case of failover)
            states = []
            for graph_ref in self._graph_refs:
                states.extend(graph_ref.get_operand_states(self._succ_keys))
            # non-terminal operand with all successors done, the data can be freed
            if all(k in OperandState.TERMINATED_STATES for k in states) and self._is_worker_alive():
                self.ref().free_data(_tell=True)