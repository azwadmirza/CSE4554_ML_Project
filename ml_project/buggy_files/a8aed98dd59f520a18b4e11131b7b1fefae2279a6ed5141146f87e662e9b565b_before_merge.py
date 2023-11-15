    def _upload(self, data):
        payload = {"op": "APPEND"}
        init_response = requests.post("http://" + self.uri_path,
                                      params=payload, allow_redirects=False)
        if not init_response.status_code == httplib.TEMPORARY_REDIRECT:
            raise WebHdfsException(str(init_response.status_code) + "\n" + init_response.content)
        uri = init_response.headers['location']
        response = requests.post(uri, data=data,
                                 headers={'content-type': 'application/octet-stream'})
        if not response.status_code == httplib.OK:
            raise WebHdfsException(str(response.status_code) + "\n" + repr(response.content))