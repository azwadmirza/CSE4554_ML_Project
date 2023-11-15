    def connection_lost(self, exc):
        if self.access_logs:
            self.logger.debug("%s - Disconnected", self.server[0])

        if self.cycle and self.cycle.more_body:
            self.cycle.disconnected = True
        self.client_event.set()