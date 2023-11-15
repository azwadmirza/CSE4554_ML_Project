    def set_operand_state(self, op_key, state):
        if op_key not in self._operand_infos and \
                self._chunk_graph_builder.iterative_chunk_graphs and \
                state == OperandState.FREED:
            # if iterative tiling is entered,
            # the `_operand_infos` will be a completely new one,
            # in this case, we don't actually care about if the op is freed
            return
        if op_key not in self._operand_infos and self.state in GraphState.TERMINATED_STATES:
            # if operand has been cleared in iterative tiling and execute again in another
            # graph, just ignore it.
            return
        op_info = self._operand_infos[op_key]
        op_info['state'] = state
        self._graph_meta_ref.update_op_state(op_key, op_info['op_name'], state,
                                             _tell=True, _wait=False)
        try:
            del op_info['failover_state']
        except KeyError:
            pass