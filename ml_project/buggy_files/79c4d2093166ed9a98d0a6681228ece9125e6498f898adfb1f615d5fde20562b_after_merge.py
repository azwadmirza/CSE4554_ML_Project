    def terminate(self):
        """Terminate the connection without waiting for pending data."""
        self._mark_stmts_as_closed()
        self._listeners.clear()
        self._log_listeners.clear()
        self._aborted = True
        self._protocol.abort()
        self._clean_tasks()