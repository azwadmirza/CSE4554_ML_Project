    def disconnect(self):
        """Disconnect session, close socket if needed."""
        if self.session is not None:
            try:
                self._eagain(self.session.disconnect)
            except Exception:
                pass
        if self.sock is not None and not self.sock.closed:
            self.sock.close()