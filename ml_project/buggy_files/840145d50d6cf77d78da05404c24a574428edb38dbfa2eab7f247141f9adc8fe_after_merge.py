    def error_received(self, exc):  # pragma: no cover
        if self.recvfrom and not self.recvfrom.done():
            self.recvfrom.set_exception(exc)