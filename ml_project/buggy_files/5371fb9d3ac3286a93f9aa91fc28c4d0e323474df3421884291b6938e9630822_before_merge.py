    def _cleanup_servers(self):
        while True:
            for client, server in self._servers.items():
                if client.sock.closed:
                    server.stop()
                    del self._servers[client]
            sleep(60)