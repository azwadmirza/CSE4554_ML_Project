    def __init__(
        self,
        thrift_url="",
        auth=None,
        client=jaeger.Client,
        http_transport=THttpClient.THttpClient,
    ):
        self.thrift_url = thrift_url
        self.auth = auth
        self.http_transport = http_transport(uri_or_host=thrift_url)
        self.client = client(
            iprot=TBinaryProtocol.TBinaryProtocol(trans=self.http_transport)
        )

        # set basic auth header
        if auth is not None:
            auth_header = "{}:{}".format(*auth)
            decoded = base64.b64encode(auth_header.encode()).decode("ascii")
            basic_auth = dict(Authorization="Basic {}".format(decoded))
            self.http_transport.setCustomHeaders(basic_auth)