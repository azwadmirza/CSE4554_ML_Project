    def connection_made(self, transport):
        """Establish connection to host."""
        log_binary(
            _LOGGER, "Sending DNS request to " + str(self.host), Data=self.message
        )

        self.transport = transport
        self.transport.sendto(self.message)