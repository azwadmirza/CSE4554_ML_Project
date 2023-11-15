    def __init__(
        self,
        *,
        token: Optional[str] = None,
        web_client: Optional[WebClient] = None,
        auto_reconnect_enabled: bool = True,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        timeout: int = 30,
        base_url: str = WebClient.BASE_URL,
        headers: Optional[dict] = None,
        ping_interval: int = 5,
        concurrency: int = 10,
        logger: Optional[logging.Logger] = None,
        on_message_listeners: Optional[List[Callable[[str], None]]] = None,
        on_error_listeners: Optional[List[Callable[[Exception], None]]] = None,
        on_close_listeners: Optional[List[Callable[[int, Optional[str]], None]]] = None,
        trace_enabled: bool = False,
        all_message_trace_enabled: bool = False,
        ping_pong_trace_enabled: bool = False,
    ):
        self.token = token.strip() if token is not None else None
        self.bot_id = None
        self.default_auto_reconnect_enabled = auto_reconnect_enabled
        # You may want temporarily turn off the auto_reconnect as necessary
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.ssl = ssl
        self.proxy = proxy
        self.timeout = timeout
        self.base_url = base_url
        self.headers = headers
        self.ping_interval = ping_interval
        self.logger = logger or logging.getLogger(__name__)
        if self.proxy is None or len(self.proxy.strip()) == 0:
            env_variable = load_http_proxy_from_env(self.logger)
            if env_variable is not None:
                self.proxy = env_variable

        self.web_client = web_client or WebClient(
            token=self.token,
            base_url=self.base_url,
            timeout=self.timeout,
            ssl=self.ssl,
            proxy=self.proxy,
            headers=self.headers,
            logger=logger,
        )

        self.on_message_listeners = on_message_listeners or []

        self.on_error_listeners = on_error_listeners or []
        self.on_close_listeners = on_close_listeners or []

        self.trace_enabled = trace_enabled
        self.all_message_trace_enabled = all_message_trace_enabled
        self.ping_pong_trace_enabled = ping_pong_trace_enabled

        self.message_queue = Queue()

        def goodbye_listener(_self, event: dict):
            if event.get("type") == "goodbye":
                message = "Got a goodbye message. Reconnecting to the server ..."
                self.logger.info(message)
                self.connect_to_new_endpoint(force=True)

        self.message_listeners = [goodbye_listener]
        self.socket_mode_request_listeners = []

        self.current_session = None
        self.current_session_state = ConnectionState()
        self.current_session_runner = IntervalRunner(
            self._run_current_session, 0.5
        ).start()
        self.wss_uri = None

        self.current_app_monitor_started = False
        self.current_app_monitor = IntervalRunner(
            self._monitor_current_session,
            self.ping_interval,
        )

        self.closed = False
        self.connect_operation_lock = Lock()

        self.message_processor = IntervalRunner(self.process_messages, 0.001).start()
        self.message_workers = ThreadPoolExecutor(max_workers=concurrency)