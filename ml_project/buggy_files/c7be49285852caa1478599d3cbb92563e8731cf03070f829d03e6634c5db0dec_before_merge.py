    def __init__(
        self,
        rpc_client: JSONRPCClient,
        proxy_manager: ProxyManager,
        query_start_block: BlockNumber,
        default_registry: TokenNetworkRegistry,
        default_secret_registry: SecretRegistry,
        default_service_registry: Optional[ServiceRegistry],
        default_one_to_n_address: Optional[OneToNAddress],
        default_msc_address: Optional[MonitoringServiceAddress],
        transport: MatrixTransport,
        raiden_event_handler: EventHandler,
        message_handler: MessageHandler,
        routing_mode: RoutingMode,
        config: RaidenConfig,
        user_deposit: UserDeposit = None,
        api_server: Optional[APIServer] = None,
    ) -> None:
        super().__init__()
        self.tokennetworkaddrs_to_connectionmanagers: ConnectionManagerDict = dict()
        self.targets_to_identifiers_to_statuses: StatusesDict = defaultdict(dict)

        self.rpc_client = rpc_client
        self.proxy_manager = proxy_manager
        self.default_registry = default_registry
        self.query_start_block = query_start_block
        self.default_one_to_n_address = default_one_to_n_address
        self.default_secret_registry = default_secret_registry
        self.default_service_registry = default_service_registry
        self.default_msc_address = default_msc_address
        self.routing_mode = routing_mode
        self.config = config

        self.signer: Signer = LocalSigner(self.rpc_client.privkey)
        self.address = self.signer.address
        self.transport = transport

        self.user_deposit = user_deposit

        self.alarm = AlarmTask(
            proxy_manager=proxy_manager, sleep_time=self.config.blockchain.query_interval
        )
        self.raiden_event_handler = raiden_event_handler
        self.message_handler = message_handler
        self.blockchain_events: Optional[BlockchainEvents] = None

        self.api_server: Optional[APIServer] = api_server
        self.raiden_api: Optional[RaidenAPI] = None
        self.rest_api: Optional[RestAPI] = None
        if api_server is not None:
            self.raiden_api = RaidenAPI(self)
            self.rest_api = api_server.rest_api

        self.stop_event = Event()
        self.stop_event.set()  # inits as stopped
        self.greenlets: List[Greenlet] = list()

        self.last_log_time = datetime.now()
        self.last_log_block = BlockNumber(0)

        self.contract_manager = ContractManager(config.contracts_path)
        self.wal: Optional[WriteAheadLog] = None

        if self.config.database_path != ":memory:":
            database_dir = os.path.dirname(config.database_path)
            os.makedirs(database_dir, exist_ok=True)

            self.database_dir: Optional[str] = database_dir

            # Two raiden processes must not write to the same database. Even
            # though it's possible the database itself would not be corrupt,
            # the node's state could. If a database was shared among multiple
            # nodes, the database WAL would be the union of multiple node's
            # WAL. During a restart a single node can't distinguish its state
            # changes from the others, and it would apply it all, meaning that
            # a node would execute the actions of itself and the others.
            #
            # Additionally the database snapshots would be corrupt, because it
            # would not represent the effects of applying all the state changes
            # in order.
            lock_file = os.path.join(self.database_dir, ".lock")
            self.db_lock = filelock.FileLock(lock_file)
        else:
            self.database_dir = None
            self.serialization_file = None
            self.db_lock = None

        self.payment_identifier_lock = gevent.lock.Semaphore()

        # A list is not hashable, so use tuple as key here
        self.route_to_feedback_token: Dict[Tuple[Address, ...], UUID] = dict()

        # Flag used to skip the processing of all Raiden events during the
        # startup.
        #
        # Rationale: At the startup, the latest snapshot is restored and all
        # state changes which are not 'part' of it are applied. The criteria to
        # re-apply the state changes is their 'absence' in the snapshot, /not/
        # their completeness. Because these state changes are re-executed
        # in-order and some of their side-effects will already have been
        # completed, the events should be delayed until the state is
        # synchronized (e.g. an open channel state change, which has already
        # been mined).
        #
        # Incomplete events, i.e. the ones which don't have their side-effects
        # applied, will be executed once the blockchain state is synchronized
        # because of the node's queues.
        self.ready_to_process_events = False