    def __init__(self,
                 conn_str: str = "",
                 secure: bool = False,
                 metadata: List[Tuple[str, str]] = None,
                 connection_retries: int = 3):
        """Initializes the worker side grpc client.

        Args:
            conn_str: The host:port connection string for the ray server.
            secure: whether to use SSL secure channel or not.
            metadata: additional metadata passed in the grpc request headers.
            connection_retries: Number of times to attempt to reconnect to the
              ray server if it doesn't respond immediately. Setting to 0 tries
              at least once.  For infinite retries, catch the ConnectionError
              exception.
        """
        self.metadata = metadata if metadata else []
        self.channel = None
        self._client_id = make_client_id()
        if secure:
            credentials = grpc.ssl_channel_credentials()
            self.channel = grpc.secure_channel(conn_str, credentials)
        else:
            self.channel = grpc.insecure_channel(conn_str)

        conn_attempts = 0
        timeout = INITIAL_TIMEOUT_SEC
        while conn_attempts < connection_retries + 1:
            conn_attempts += 1
            try:
                grpc.channel_ready_future(self.channel).result(timeout=timeout)
                break
            except grpc.FutureTimeoutError:
                if conn_attempts >= connection_retries:
                    raise ConnectionError("ray client connection timeout")
                logger.info(f"Couldn't connect in {timeout} seconds, retrying")
                timeout = timeout + 5
                if timeout > MAX_TIMEOUT_SEC:
                    timeout = MAX_TIMEOUT_SEC

        self.server = ray_client_pb2_grpc.RayletDriverStub(self.channel)

        self.data_client = DataClient(self.channel, self._client_id,
                                      self.metadata)
        self.reference_count: Dict[bytes, int] = defaultdict(int)

        self.log_client = LogstreamClient(self.channel, self.metadata)
        self.log_client.set_logstream_level(logging.INFO)
        self.closed = False