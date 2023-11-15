    def connection_made(self, transport):
        """Establish connection to host."""
        self.transport = transport
        self._task = asyncio.ensure_future(self._resend_loop())