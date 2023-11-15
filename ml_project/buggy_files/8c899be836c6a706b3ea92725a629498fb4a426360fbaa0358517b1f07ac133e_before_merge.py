    def __init__(self, client, host, port, bind_address='127.0.0.1', timeout=0.1):
        StreamServer.__init__(self, (bind_address, 0), self._read_rw)
        self.client = client
        self.host = host
        self.port = port
        self.session = client.session
        self._retries = DEFAULT_RETRIES
        self.timeout = timeout