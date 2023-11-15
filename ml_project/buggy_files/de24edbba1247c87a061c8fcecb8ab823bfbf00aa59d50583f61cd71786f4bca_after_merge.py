    def __init__(
        self,
        socket: BaseSocketStream,
        backend: typing.Union[str, ConcurrencyBackend] = "auto",
        on_release: typing.Callable = None,
    ):
        self.socket = socket
        self.backend = lookup_backend(backend)
        self.on_release = on_release
        self.state = h2.connection.H2Connection(config=self.CONFIG)

        self.streams = {}  # type: typing.Dict[int, HTTP2Stream]
        self.events = {}  # type: typing.Dict[int, typing.List[h2.events.Event]]

        self.sent_connection_init = False