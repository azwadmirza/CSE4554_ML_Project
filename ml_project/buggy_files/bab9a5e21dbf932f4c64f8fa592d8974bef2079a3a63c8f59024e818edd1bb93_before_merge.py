    def close(self):
        if self.conn and not self._closed:
            self.conn.shutdown(socket.SHUT_RDWR)
        self._closed = True