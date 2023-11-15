    def __init__(
        self,
        *,
        token: str,
        run_async: Optional[bool] = False,
        auto_reconnect: Optional[bool] = True,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        timeout: Optional[int] = 30,
        base_url: Optional[str] = WebClient.BASE_URL,
        connect_method: Optional[str] = None,
        ping_interval: Optional[int] = 30,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        headers: Optional[dict] = {},
    ):
        self.token = token.strip()
        self.run_async = run_async
        self.auto_reconnect = auto_reconnect
        self.ssl = ssl
        self.proxy = proxy
        self.timeout = timeout
        self.base_url = base_url
        self.connect_method = connect_method
        self.ping_interval = ping_interval
        self.headers = headers
        self._event_loop = loop or asyncio.get_event_loop()
        self._web_client = None
        self._websocket = None
        self._session = None
        self._logger = logging.getLogger(__name__)
        self._last_message_id = 0
        self._connection_attempts = 0
        self._stopped = False
        self._web_client = WebClient(
            token=self.token,
            base_url=self.base_url,
            timeout=self.timeout,
            ssl=self.ssl,
            proxy=self.proxy,
            run_async=self.run_async,
            loop=self._event_loop,
            session=self._session,
            headers=self.headers,
        )