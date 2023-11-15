    def _request(self, path, method='GET', data=None, headers=None, params=None):
        logger.info("%s %s", method, path)
        url = self.base_url + path
        headers = headers or {}
        params = params or {}
        if self.cookie:
            headers['Cookie'] = self.cookie

        try:
            response = requests.request(method, url, data=data, headers=headers,
                                        params=params)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            raise OLError(e)