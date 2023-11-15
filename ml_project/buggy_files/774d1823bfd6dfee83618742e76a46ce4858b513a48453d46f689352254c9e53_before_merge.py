    def _get_auth(self):

        post_data = json.dumps({
            'method': 'session-get',
        })

        self.response = self.session.post(self.url, data=post_data.encode('utf-8'), timeout=120,
                                          verify=app.TORRENT_VERIFY_CERT)
        self.auth = re.search(r'X-Transmission-Session-Id:\s*(\w+)', self.response.text).group(1)

        self.session.headers.update({'x-transmission-session-id': self.auth})

        # Validating Transmission authorization
        post_data = json.dumps({
            'arguments': {},
            'method': 'session-get',
        })

        self._request(method='post', data=post_data)

        return self.auth