    def append_graph(self, graph_key, op_info):
        super().append_graph(graph_key, op_info)

        if not self._is_terminal:
            self._is_terminal = op_info.get('is_terminal')

        if self.state not in OperandState.TERMINATED_STATES:
            for in_key in self._pred_keys:
                self._get_operand_actor(in_key).remove_finished_successor(
                    self._op_key, _tell=True, _wait=False)
            self.start_operand()
        elif self.state in OperandState.STORED_STATES:
            for out_key in self._succ_keys:
                self._get_operand_actor(out_key).add_finished_predecessor(
                    self._op_key, self.worker, output_sizes=self._data_sizes,
                    output_shapes=self._data_shapes, _tell=True, _wait=False)
            # require more chunks to execute if the completion caused no successors to run
            if self._is_terminal:
                # update records in GraphActor to help decide if the whole graph finished execution
                self._add_finished_terminal()