    def __init__(self, hosts, user=None, password=None, port=None, pkey=None,
                 allow_agent=True,
                 num_retries=DEFAULT_RETRIES,
                 timeout=120, pool_size=10,
                 host_config=None, retry_delay=RETRY_DELAY):
        if isinstance(hosts, str) or isinstance(hosts, bytes):
            raise TypeError(
                "Hosts must be list or other iterable, not string. "
                "For example: ['localhost'] not 'localhost'.")
        self.allow_agent = allow_agent
        self.pool_size = pool_size
        self.pool = gevent.pool.Pool(size=self.pool_size)
        self.hosts = hosts
        self.user = user
        self.password = password
        self.port = port
        self.pkey = pkey
        self.num_retries = num_retries
        self.timeout = timeout
        # To hold host clients
        self.host_clients = {}
        self.host_config = host_config if host_config else {}
        self.retry_delay = retry_delay
        self.cmds = None