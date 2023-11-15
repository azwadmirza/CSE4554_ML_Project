    def __init__(
        self,
        address=None,
        loop=None,
        timeout=no_default,
        set_as_default=True,
        scheduler_file=None,
        security=None,
        asynchronous=False,
        name=None,
        heartbeat_interval=None,
        serializers=None,
        deserializers=None,
        extensions=DEFAULT_EXTENSIONS,
        direct_to_workers=None,
        connection_limit=512,
        **kwargs,
    ):
        if timeout == no_default:
            timeout = dask.config.get("distributed.comm.timeouts.connect")
        if timeout is not None:
            timeout = parse_timedelta(timeout, "s")
        self._timeout = timeout

        self.futures = dict()
        self.refcount = defaultdict(lambda: 0)
        self.coroutines = []
        if name is None:
            name = dask.config.get("client-name", None)
        self.id = (
            type(self).__name__
            + ("-" + name + "-" if name else "-")
            + str(uuid.uuid1(clock_seq=os.getpid()))
        )
        self.generation = 0
        self.status = "newly-created"
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

        # Communication
        self.scheduler_comm = None

        if address is None:
            address = dask.config.get("scheduler-address", None)
            if address:
                logger.info("Config value `scheduler-address` found: %s", address)

        if address is not None and kwargs:
            raise ValueError(
                "Unexpected keyword arguments: {}".format(str(sorted(kwargs)))
            )

        if isinstance(address, (rpc, PooledRPCCall)):
            self.scheduler = address
        elif isinstance(getattr(address, "scheduler_address", None), str):
            # It's a LocalCluster or LocalCluster-compatible object
            self.cluster = address
            with suppress(AttributeError):
                loop = address.loop
            if security is None:
                security = getattr(self.cluster, "security", None)
        elif address is not None and not isinstance(address, str):
            raise TypeError(
                "Scheduler address must be a string or a Cluster instance, got {}".format(
                    type(address)
                )
            )

        if security is None:
            security = Security()
        elif security is True:
            security = Security.temporary()
            self._startup_kwargs["security"] = security
        elif not isinstance(security, Security):
            raise TypeError("security must be a Security object")

        self.security = security

        if name == "worker":
            self.connection_args = self.security.get_connection_args("worker")
        else:
            self.connection_args = self.security.get_connection_args("client")

        self._connecting_to_scheduler = False
        self._asynchronous = asynchronous
        self._should_close_loop = not loop
        self._loop_runner = LoopRunner(loop=loop, asynchronous=asynchronous)
        self.io_loop = self.loop = self._loop_runner.loop

        self._gather_keys = None
        self._gather_future = None

        if heartbeat_interval is None:
            heartbeat_interval = dask.config.get("distributed.client.heartbeat")
        heartbeat_interval = parse_timedelta(heartbeat_interval, default="ms")

        scheduler_info_interval = parse_timedelta(
            dask.config.get("distributed.client.scheduler-info-interval", default="ms")
        )

        self._periodic_callbacks = dict()
        self._periodic_callbacks["scheduler-info"] = PeriodicCallback(
            self._update_scheduler_info, scheduler_info_interval * 1000,
        )
        self._periodic_callbacks["heartbeat"] = PeriodicCallback(
            self._heartbeat, heartbeat_interval * 1000
        )

        self._start_arg = address
        if set_as_default:
            self._set_config = dask.config.set(
                scheduler="dask.distributed", shuffle="tasks"
            )

        self._stream_handlers = {
            "key-in-memory": self._handle_key_in_memory,
            "lost-data": self._handle_lost_data,
            "cancelled-key": self._handle_cancelled_key,
            "task-retried": self._handle_retried_key,
            "task-erred": self._handle_task_erred,
            "restart": self._handle_restart,
            "error": self._handle_error,
        }

        self._state_handlers = {
            "memory": self._handle_key_in_memory,
            "lost": self._handle_lost_data,
            "erred": self._handle_task_erred,
        }

        self.rpc = ConnectionPool(
            limit=connection_limit,
            serializers=serializers,
            deserializers=deserializers,
            deserialize=True,
            connection_args=self.connection_args,
            timeout=timeout,
            server=self,
        )

        for ext in extensions:
            ext(self)

        self.start(timeout=timeout)
        Client._instances.add(self)

        from distributed.recreate_exceptions import ReplayExceptionClient

        ReplayExceptionClient(self)