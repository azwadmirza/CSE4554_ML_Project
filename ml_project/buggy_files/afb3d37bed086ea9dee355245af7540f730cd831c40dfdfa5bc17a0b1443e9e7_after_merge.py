    def __init__(self, uri):
        self._uri = uri

        payload = {"op": "OPEN", "offset": 0}
        self._response = requests.get(self._uri, params=payload, stream=True)
        if self._response.status_code != httplib.OK:
            raise WebHdfsException.from_response(self._response)
        self._buf = b''