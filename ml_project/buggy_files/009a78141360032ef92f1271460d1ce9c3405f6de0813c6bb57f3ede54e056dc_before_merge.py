    def _add_finished_terminal(self, final_state=None, exc=None):
        futures = []
        for graph_ref in self._graph_refs:
            futures.append(graph_ref.add_finished_terminal(
                self._op_key, final_state=final_state, exc=exc, _tell=True, _wait=False
            ))

        return futures