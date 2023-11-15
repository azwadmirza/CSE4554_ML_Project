    def error_received(self, exc):  # pragma: no cover
        if self.recvfrom:
            self.recvfrom.set_exception(exc)