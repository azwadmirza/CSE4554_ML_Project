    def __init__(self, host, fw_host, fw_port, user=None,
                 password=None, port=None, pkey=None,
                 num_retries=DEFAULT_RETRIES,
                 retry_delay=RETRY_DELAY,
                 allow_agent=True, timeout=None, listen_port=0):
        Thread.__init__(self)
        self.client = None
        self.session = None
        self.socket = None
        self.listen_port = listen_port
        self.fw_host = fw_host
        self.fw_port = fw_port if fw_port else 22
        self.channel = None
        self.forward_sock = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.pkey = pkey
        self.num_retries = num_retries
        self.retry_delay = retry_delay
        self.allow_agent = allow_agent
        self.timeout = timeout
        self.exception = None
        self.tunnel_open = Event()