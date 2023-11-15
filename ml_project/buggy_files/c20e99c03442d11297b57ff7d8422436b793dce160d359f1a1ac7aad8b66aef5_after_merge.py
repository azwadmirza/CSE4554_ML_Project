    def __init__(self, thrift_url="", auth=None):
        self.thrift_url = thrift_url
        self.auth = auth
        self.http_transport = THttpClient.THttpClient(
            uri_or_host=self.thrift_url
        )
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.http_transport)

        # set basic auth header
        if auth is not None:
            auth_header = "{}:{}".format(*auth)
            decoded = base64.b64encode(auth_header.encode()).decode("ascii")
            basic_auth = dict(Authorization="Basic {}".format(decoded))
            self.http_transport.setCustomHeaders(basic_auth)