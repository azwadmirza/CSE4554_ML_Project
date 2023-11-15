    def __init__(self):
        """Thread runner for a group of local port forwarding proxies.

        Starts servers in their own gevent hub via thread run target.

        Use ``enqueue`` to create new servers
        and get port to connect to via ``out_q`` once a target has been put into the input queue.

        ``SSHClient`` is the client for the SSH host that will be proxying.
        """
        Thread.__init__(self)
        self.in_q = Queue(1)
        self.out_q = Queue(1)
        self._servers = {}
        self._hub = None
        self.started = Event()
        self._cleanup_let = None