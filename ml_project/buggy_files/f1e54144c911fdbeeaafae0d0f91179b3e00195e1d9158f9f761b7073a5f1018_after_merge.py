    def _get_auth(self):
        try:
            self.response = self.session.get(urljoin(self.url, 'token.html'), verify=False)
        except RequestException as error:
            log.warning('Unable to authenticate with uTorrent client: {0!r}', error)
            return None

        if not self.response.status_code == 404:
            self.auth = re.findall('<div.*?>(.*?)</', self.response.text)[0]
            return self.auth

        return None