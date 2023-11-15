    def __init__(self, client, host, port, bind_address='127.0.0.1',
                 num_retries=DEFAULT_RETRIES):
        StreamServer.__init__(self, (bind_address, 0), self._read_rw)
        self.client = client
        self.host = host
        self.port = port
        self.session = client.session
        self._client = client
        self._retries = num_retries
        self.bind_address = bind_address