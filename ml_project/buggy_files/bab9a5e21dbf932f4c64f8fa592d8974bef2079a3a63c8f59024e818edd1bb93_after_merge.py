    def close(self):
        if self.conn and not self._closed:
            try:
                # May already be closed despite self._closed == False if a network error occurred and `close` is being
                # called as part of cleanup.
                self.conn.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
        self._closed = True