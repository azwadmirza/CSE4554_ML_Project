    def close(self, client_only=False):
        if self.conn:
            self.conn.close()

        if not client_only:
            try:
                self.socket.shutdown(2)
            except (OSError, socket.error):
                pass
            self.socket.close()