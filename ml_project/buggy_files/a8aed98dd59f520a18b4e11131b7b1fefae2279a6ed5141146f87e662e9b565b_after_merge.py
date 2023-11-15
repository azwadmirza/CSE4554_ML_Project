    def _upload(self, data):
        payload = {"op": "APPEND"}
        init_response = requests.post(self._uri, params=payload, allow_redirects=False)
        if not init_response.status_code == httplib.TEMPORARY_REDIRECT:
            raise WebHdfsException.from_response(init_response)
        uri = init_response.headers['location']
        response = requests.post(uri, data=data,
                                 headers={'content-type': 'application/octet-stream'})
        if not response.status_code == httplib.OK:
            raise WebHdfsException.from_response(response)