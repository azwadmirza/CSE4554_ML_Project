    def cleanup(self):
        # close active persistent connections
        for sock in itervalues(self._active_connections):
            conn = Connection(sock)
            conn.reset()
        self._final_q.put(_sentinel)
        self._results_thread.join()