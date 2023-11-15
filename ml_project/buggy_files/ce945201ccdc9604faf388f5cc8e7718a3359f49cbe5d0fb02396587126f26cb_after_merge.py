    def shutdown(self):
        """Stop all tunnel servers."""
        for client, server in self._servers.items():
            server.stop()