    def connection_lost(self, exc):
        if self.recvfrom:
            self.recvfrom.set_exception(exc)