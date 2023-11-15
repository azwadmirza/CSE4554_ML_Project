    def __init__(
            self,
            type: str,
            client_conn: connections.ClientConnection,
            server_conn: connections.ServerConnection,
            live=None
    ):
        self.type = type
        self.id = str(uuid.uuid4())
        self.client_conn = client_conn
        self.server_conn = server_conn
        self.live = live

        self.error = None  # type: Optional[Error]
        self.intercepted = False  # type: bool
        self._backup = None  # type: Optional[Flow]
        self.reply = None
        self.marked = False  # type: bool