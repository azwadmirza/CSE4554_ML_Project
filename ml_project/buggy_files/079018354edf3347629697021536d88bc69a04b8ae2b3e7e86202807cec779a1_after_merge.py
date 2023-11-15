    def connection_lost(self, exc):
        if self.recvfrom and not self.recvfrom.done():
            self.recvfrom.set_exception(exc)