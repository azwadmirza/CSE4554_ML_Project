    def disconnect(self):
        """Disconnect session, close socket if needed."""
        logger.debug("Disconnecting client for host %s", self.host)
        if self.session is not None:
            try:
                self._eagain(self.session.disconnect)
            except Exception:
                pass
        if self.sock is not None and not self.sock.closed:
            self.sock.close()
            logger.debug("Client socket closed for host %s", self.host)