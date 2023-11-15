    def _call_write(self, name, query, comment, action):
        headers = {'Content-Type': 'application/json'}
        query = marshal(query)

        # use HTTP Extension Framework to add custom headers. see RFC 2774 for more details.
        if comment or action:
            headers['Opt'] = '"%s/dev/docs/api"; ns=42' % self.base_url
        if comment:
            headers['42-comment'] = comment
        if action:
            headers['42-action'] = action

        response = self._request('/api/' + name, method="POST", data=json.dumps(query), headers=headers)
        return response.json()