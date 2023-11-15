    def _close_client(self, id_):
        client = self._client_by_id(id_)
        self.clients.pop(client, None)
        if client:
            client.close()