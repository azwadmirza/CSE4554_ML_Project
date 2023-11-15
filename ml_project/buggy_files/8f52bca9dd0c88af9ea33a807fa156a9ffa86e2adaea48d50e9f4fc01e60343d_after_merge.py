    def __init__(
        self,
        stream_reader: asyncio.StreamReader,
        stream_writer: asyncio.StreamWriter,
        timeout: TimeoutConfig,
    ):
        self.stream_reader = stream_reader
        self.stream_writer = stream_writer
        self.timeout = timeout
        self.read_lock = asyncio.Lock()

        self._inner: typing.Optional[SocketStream] = None