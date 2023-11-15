    def __init__(self, uri):
        self._uri = uri

        payload = {"op": "OPEN", "offset": 0}
        self._response = requests.get("http://" + self._uri, params=payload, stream=True)
        self._buf = b''