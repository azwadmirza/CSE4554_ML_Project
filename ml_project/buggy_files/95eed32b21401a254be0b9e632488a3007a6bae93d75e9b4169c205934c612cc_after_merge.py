    def save(self, key, data, comment=None):
        headers = {'Content-Type': 'application/json'}
        data = marshal(data)
        if comment:
            headers['Opt'] = '"%s/dev/docs/api"; ns=42' % self.base_url
            headers['42-comment'] = comment
        data = json.dumps(data)
        return self._request(key, method="PUT", data=data, headers=headers).content