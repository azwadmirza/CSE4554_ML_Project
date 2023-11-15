    def __init__(
            self,
            token: base.String,
            loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None,
            connections_limit: Optional[base.Integer] = None,
            proxy: Optional[base.String] = None,
            proxy_auth: Optional[aiohttp.BasicAuth] = None,
            validate_token: Optional[base.Boolean] = True,
            parse_mode: typing.Optional[base.String] = None,
            timeout: typing.Optional[typing.Union[base.Integer, base.Float, aiohttp.ClientTimeout]] = None
    ):
        """
        Instructions how to get Bot token is found here: https://core.telegram.org/bots#3-how-do-i-create-a-bot

        :param token: token from @BotFather
        :type token: :obj:`str`
        :param loop: event loop
        :type loop: Optional Union :obj:`asyncio.BaseEventLoop`, :obj:`asyncio.AbstractEventLoop`
        :param connections_limit: connections limit for aiohttp.ClientSession
        :type connections_limit: :obj:`int`
        :param proxy: HTTP proxy URL
        :type proxy: :obj:`str`
        :param proxy_auth: Authentication information
        :type proxy_auth: Optional :obj:`aiohttp.BasicAuth`
        :param validate_token: Validate token.
        :type validate_token: :obj:`bool`
        :param parse_mode: You can set default parse mode
        :type parse_mode: :obj:`str`
        :param timeout: Request timeout
        :type timeout: :obj:`typing.Optional[typing.Union[base.Integer, base.Float, aiohttp.ClientTimeout]]`
        :raise: when token is invalid throw an :obj:`aiogram.utils.exceptions.ValidationError`
        """
        # Authentication
        if validate_token:
            api.check_token(token)
        self._token = None
        self.__token = token
        self.id = int(token.split(sep=':')[0])

        self.proxy = proxy
        self.proxy_auth = proxy_auth

        # Asyncio loop instance
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

        # aiohttp main session
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_class: Type[aiohttp.TCPConnector] = aiohttp.TCPConnector
        self._connector_init = dict(
            limit=connections_limit, ssl=ssl_context, loop=self.loop
        )

        if isinstance(proxy, str) and (proxy.startswith('socks5://') or proxy.startswith('socks4://')):
            from aiohttp_socks import SocksConnector
            from aiohttp_socks.utils import parse_proxy_url

            socks_ver, host, port, username, password = parse_proxy_url(proxy)
            if proxy_auth:
                if not username:
                    username = proxy_auth.login
                if not password:
                    password = proxy_auth.password

            self._connector_class = SocksConnector
            self._connector_init.update(
                socks_ver=socks_ver, host=host, port=port,
                username=username, password=password, rdns=True,
            )
            self.proxy = None
            self.proxy_auth = None

        self._timeout = None
        self.timeout = timeout

        self.parse_mode = parse_mode