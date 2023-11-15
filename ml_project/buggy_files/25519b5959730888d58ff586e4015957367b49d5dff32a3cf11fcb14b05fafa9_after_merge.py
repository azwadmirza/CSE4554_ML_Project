    def set(self, key, value):
        key = string(key)
        request_parameters = self._prepare_put_request(key, value)
        self.client.put_item(**request_parameters)