    def get(self, key, v=None):
        data = self._request(key + '.json' + ('?v=%d' % v if v else '')).read()
        return unmarshal(json.loads(data))