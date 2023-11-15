    def __init__(self, raw_client_hello):
        self._client_hello = _constructs.ClientHello.parse(raw_client_hello)