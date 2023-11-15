    def append_graph(self, graph_key, op_info):
        from ..graph import GraphActor

        if not self._is_terminal:
            self._is_terminal = op_info.get('is_terminal')
        graph_ref = self.get_actor_ref(GraphActor.gen_uid(self._session_id, graph_key))
        self._graph_refs.append(graph_ref)
        self._pred_keys.update(op_info['io_meta']['predecessors'])
        self._succ_keys.update(op_info['io_meta']['successors'])
        if self._state not in OperandState.STORED_STATES and self._state != OperandState.RUNNING:
            self._state = op_info['state']