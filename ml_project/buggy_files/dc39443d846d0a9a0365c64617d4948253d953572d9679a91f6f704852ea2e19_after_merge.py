    def get(self, key, v=None):
        response = self._request(key + '.json', params={'v': v} if v else {})
        return unmarshal(response.json())