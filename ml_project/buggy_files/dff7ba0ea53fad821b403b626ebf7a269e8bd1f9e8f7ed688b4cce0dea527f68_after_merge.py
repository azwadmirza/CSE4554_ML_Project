    def _get_many(self, keys):
        response = self._request("/api/get_many", params={"keys": json.dumps(keys)})
        return response.json()['result']