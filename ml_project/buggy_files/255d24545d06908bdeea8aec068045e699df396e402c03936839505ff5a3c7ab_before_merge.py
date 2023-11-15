    def __init__(
        self,
        stream: typing.Union[trio.SocketStream, trio.SSLStream],
        timeout: TimeoutConfig,
    ) -> None:
        self.stream = stream
        self.timeout = timeout
        self.write_buffer = b""
        self.write_lock = trio.Lock()