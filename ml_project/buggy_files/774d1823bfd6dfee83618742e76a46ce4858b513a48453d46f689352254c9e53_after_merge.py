    def _get_auth(self):

        post_data = json.dumps({
            'method': 'session-get',
        })

        try:
            self.response = self.session.post(self.url, data=post_data.encode('utf-8'), timeout=120,
                                              verify=app.TORRENT_VERIFY_CERT)
        except requests.exceptions.ConnectionError as error:
            log.warning('{name}: Unable to connect. {error}',
                        {'name': self.name, 'error': error})
            return False
        except requests.exceptions.Timeout as error:
            log.warning('{name}: Connection timed out. {error}',
                        {'name': self.name, 'error': error})
            return False

        self.auth = re.search(r'X-Transmission-Session-Id:\s*(\w+)', self.response.text).group(1)

        self.session.headers.update({'x-transmission-session-id': self.auth})

        # Validating Transmission authorization
        post_data = json.dumps({
            'arguments': {},
            'method': 'session-get',
        })

        self._request(method='post', data=post_data)

        return self.auth