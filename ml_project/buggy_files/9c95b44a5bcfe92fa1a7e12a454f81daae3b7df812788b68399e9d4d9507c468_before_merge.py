    def _request(self, path, method='GET', data=None, headers=None):
        logger.info("%s %s", method, path)
        url = self.base_url + path
        headers = headers or {}
        if self.cookie:
            headers['Cookie'] = self.cookie

        try:
            req = urllib.request.Request(url, data, headers)
            req.get_method = lambda: method
            return urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            raise OLError(e)