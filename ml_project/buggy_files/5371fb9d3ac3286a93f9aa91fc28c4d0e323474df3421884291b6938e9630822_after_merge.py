    def _cleanup_servers(self):
        for client in list(self._servers.keys()):
            server = self._servers[client]
            if client.sock is None or client.sock.closed:
                server.stop()
                del self._servers[client]