        def _handle_success(*_):
            self._notify_successors(session_id, graph_key)
            self._invoke_finish_callbacks(session_id, graph_key)