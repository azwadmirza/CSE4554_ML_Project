    def cleanup(self):
        # close active persistent connections
        for sock in itervalues(self._active_connections):
            try:
                conn = Connection(sock)
                conn.reset()
            except ConnectionError as e:
                # most likely socket is already closed
                display.debug("got an error while closing persistent connection: %s" % e)
        self._final_q.put(_sentinel)
        self._results_thread.join()