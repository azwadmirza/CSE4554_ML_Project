    def __init__(self, address=None, loop=None, timeout=no_default,
                 set_as_default=True, scheduler_file=None,
                 security=None, asynchronous=False,
                 name=None, heartbeat_interval=None,
                 serializers=None, deserializers=None,
                 extensions=DEFAULT_EXTENSIONS, direct_to_workers=False,
                 **kwargs):
        if timeout == no_default:
            timeout = dask.config.get('distributed.comm.timeouts.connect')
        if timeout is not None:
            timeout = parse_timedelta(timeout, 's')
        self._timeout = timeout

        self.futures = dict()
        self.refcount = defaultdict(lambda: 0)
        self.coroutines = []
        if name is None:
            name = dask.config.get('client-name', None)
        self.id = type(self).__name__ + ('-' + name + '-' if name else '-') + str(uuid.uuid1(clock_seq=os.getpid()))
        self.generation = 0
        self.status = 'newly-created'
        self._pending_msg_buffer = []
        self.extensions = {}
        self.scheduler_file = scheduler_file
        self._startup_kwargs = kwargs
        self.cluster = None
        self.scheduler = None
        self._scheduler_identity = {}
        # A reentrant-lock on the refcounts for futures associated with this
        # client. Should be held by individual operations modifying refcounts,
        # or any bulk operation that needs to ensure the set of futures doesn't
        # change during operation.
        self._refcount_lock = threading.RLock()
        self.datasets = Datasets(self)
        self._serializers = serializers
        if deserializers is None:
            deserializers = serializers
        self._deserializers = deserializers
        self.direct_to_workers = direct_to_workers

        self._gather_semaphore = Semaphore(5)
        self._gather_keys = None
        self._gather_future = None

        # Communication
        self.security = security or Security()
        self.scheduler_comm = None
        assert isinstance(self.security, Security)

        if name == 'worker':
            self.connection_args = self.security.get_connection_args('worker')
        else:
            self.connection_args = self.security.get_connection_args('client')

        self._connecting_to_scheduler = False
        self._asynchronous = asynchronous
        self._should_close_loop = not loop
        self._loop_runner = LoopRunner(loop=loop, asynchronous=asynchronous)
        self.loop = self._loop_runner.loop

        if heartbeat_interval is None:
            heartbeat_interval = dask.config.get('distributed.client.heartbeat')
        heartbeat_interval = parse_timedelta(heartbeat_interval, default='ms')

        self._periodic_callbacks = dict()
        self._periodic_callbacks['scheduler-info'] = PeriodicCallback(
                self._update_scheduler_info, 2000, io_loop=self.loop
        )
        self._periodic_callbacks['heartbeat'] = PeriodicCallback(
                self._heartbeat,
                heartbeat_interval * 1000,
                io_loop=self.loop
        )

        if address is None:
            address = dask.config.get('scheduler-address', None)
            if address:
                logger.info("Config value `scheduler-address` found: %s",
                            address)

        if isinstance(address, (rpc, PooledRPCCall)):
            self.scheduler = address
        elif hasattr(address, "scheduler_address"):
            # It's a LocalCluster or LocalCluster-compatible object
            self.cluster = address

        self._start_arg = address
        if set_as_default:
            self._previous_scheduler = dask.config.get('scheduler', None)
            dask.config.set(scheduler='dask.distributed')

            self._previous_shuffle = dask.config.get('shuffle', None)
            dask.config.set(shuffle='tasks')

        self._stream_handlers = {
            'key-in-memory': self._handle_key_in_memory,
            'lost-data': self._handle_lost_data,
            'cancelled-key': self._handle_cancelled_key,
            'task-retried': self._handle_retried_key,
            'task-erred': self._handle_task_erred,
            'restart': self._handle_restart,
            'error': self._handle_error
        }

        self._state_handlers = {
            'memory': self._handle_key_in_memory,
            'lost': self._handle_lost_data,
            'erred': self._handle_task_erred
        }

        super(Client, self).__init__(connection_args=self.connection_args,
                                     io_loop=self.loop,
                                     serializers=serializers,
                                     deserializers=deserializers)

        for ext in extensions:
            ext(self)

        self.start(timeout=timeout)

        from distributed.recreate_exceptions import ReplayExceptionClient
        ReplayExceptionClient(self)