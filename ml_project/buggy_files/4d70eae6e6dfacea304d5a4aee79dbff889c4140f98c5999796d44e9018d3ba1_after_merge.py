    def __init__(
        self,
        url: str,
        logger: Logger,
        proxy: Optional[str] = None,
        proxy_headers: Optional[Dict[str, str]] = None,
        ping_interval: float = 5,  # seconds
        receive_timeout: float = 3,
        receive_buffer_size: int = 1024,
        trace_enabled: bool = False,
        all_message_trace_enabled: bool = False,
        ping_pong_trace_enabled: bool = False,
        on_message_listener: Optional[Callable[[str], None]] = None,
        on_error_listener: Optional[Callable[[Exception], None]] = None,
        on_close_listener: Optional[Callable[[int, Optional[str]], None]] = None,
        connection_type_name: str = "Socket Mode",
    ):
        self.url = url
        self.logger = logger
        self.proxy = proxy
        self.proxy_headers = proxy_headers

        self.ping_interval = ping_interval
        self.receive_timeout = receive_timeout
        self.receive_buffer_size = receive_buffer_size
        if self.receive_buffer_size < 16:
            raise SlackClientConfigurationError(
                "Too small receive_buffer_size detected."
            )

        self.session_id = str(uuid4())
        self.trace_enabled = trace_enabled
        self.all_message_trace_enabled = all_message_trace_enabled
        self.ping_pong_trace_enabled = ping_pong_trace_enabled
        self.last_ping_pong_time = None
        self.consecutive_check_state_error_count = 0
        self.sock = None
        # To avoid ssl.SSLError: [SSL: BAD_LENGTH] bad length
        self.sock_receive_lock = Lock()
        self.sock_send_lock = Lock()

        self.on_message_listener = on_message_listener
        self.on_error_listener = on_error_listener
        self.on_close_listener = on_close_listener
        self.connection_type_name = connection_type_name