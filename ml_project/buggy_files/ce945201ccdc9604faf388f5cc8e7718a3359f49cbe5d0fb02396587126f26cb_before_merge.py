    def shutdown(self):
        for client, server in self._servers.items():
            server.stop()