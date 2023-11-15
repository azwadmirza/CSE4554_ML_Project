    def _get_auth(self):
        self.response = self.session.get(urljoin(self.url, 'token.html'), verify=False)
        if not self.response.status_code == 404:
            self.auth = re.findall('<div.*?>(.*?)</', self.response.text)[0]
            return self.auth