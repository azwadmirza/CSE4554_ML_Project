    def _get_many(self, keys):
        response = self._request("/api/get_many?" + urllib.parse.urlencode({"keys": json.dumps(keys)}))
        return json.loads(response.read())['result']