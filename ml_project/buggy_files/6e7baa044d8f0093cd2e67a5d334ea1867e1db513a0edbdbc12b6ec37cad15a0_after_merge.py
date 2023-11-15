    def __init__(self, raw_client_hello):
        self._client_hello = tls_parser.ClientHello.parse(raw_client_hello)