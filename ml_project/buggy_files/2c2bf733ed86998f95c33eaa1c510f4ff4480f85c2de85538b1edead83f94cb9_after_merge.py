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

        # Retry the connection until the channel responds to something
        # looking like a gRPC connection, though it may be a proxy.
        conn_attempts = 0
        timeout = INITIAL_TIMEOUT_SEC
        ray_ready = False
        while conn_attempts < max(connection_retries, 1):
            conn_attempts += 1
            try:
                # Let gRPC wait for us to see if the channel becomes ready.
                # If it throws, we couldn't connect.
                grpc.channel_ready_future(self.channel).result(timeout=timeout)
                # The HTTP2 channel is ready. Wrap the channel with the
                # RayletDriverStub, allowing for unary requests.
                self.server = ray_client_pb2_grpc.RayletDriverStub(
                    self.channel)
                # Now the HTTP2 channel is ready, or proxied, but the
                # servicer may not be ready. Call is_initialized() and if
                # it throws, the servicer is not ready. On success, the
                # `ray_ready` result is checked.
                ray_ready = self.is_initialized()
                if ray_ready:
                    # Ray is ready! Break out of the retry loop
                    break
                # Ray is not ready yet, wait a timeout
                time.sleep(timeout)
            except grpc.FutureTimeoutError:
                logger.info(
                    f"Couldn't connect channel in {timeout} seconds, retrying")
                # Note that channel_ready_future constitutes its own timeout,
                # which is why we do not sleep here.
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    # UNAVAILABLE is gRPC's retryable error,
                    # so we do that here.
                    logger.info("Ray client server unavailable, "
                                f"retrying in {timeout}s...")
                    logger.debug(f"Received when checking init: {e.details()}")
                    # Ray is not ready yet, wait a timeout
                    time.sleep(timeout)
                else:
                    # Any other gRPC error gets a reraise
                    raise e
            # Fallthrough, backoff, and retry at the top of the loop
            logger.info("Waiting for Ray to become ready on the server, "
                        f"retry in {timeout}s...")
            timeout = backoff(timeout)

        # If we made it through the loop without ray_ready it means we've used
        # up our retries and should error back to the user.
        if not ray_ready:
            raise ConnectionError("ray client connection timeout")

        # Initialize the streams to finish protocol negotiation.
        self.data_client = DataClient(self.channel, self._client_id,
                                      self.metadata)
        self.reference_count: Dict[bytes, int] = defaultdict(int)

        self.log_client = LogstreamClient(self.channel, self.metadata)
        self.log_client.set_logstream_level(logging.INFO)
        self.closed = False