    def disconnect(self):
        """Disconnect session, close socket if needed."""
        self._keepalive_greenlet = None
        if self.session is not None:
            try:
                self._eagain(self.session.disconnect)
            except Exception:
                pass
            self.session = None
        self.sock = None