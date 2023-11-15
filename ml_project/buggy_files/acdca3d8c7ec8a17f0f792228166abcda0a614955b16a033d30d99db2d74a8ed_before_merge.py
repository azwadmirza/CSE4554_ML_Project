    def close(self, client_only=False):
        if self.conn:
            self.conn.close()

        if not client_only:
            self.socket.shutdown(2)
            self.socket.close()