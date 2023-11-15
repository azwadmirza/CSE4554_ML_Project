    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Init all variables and objects the bot needs to work
        :param config: configuration dict, you can use Configuration.get_config()
        to get the config dict.
        """

        logger.info('Starting freqtrade %s', __version__)

        # Init bot state
        self.state = State.STOPPED

        # Init objects
        self.config = config

        self.strategy: IStrategy = StrategyResolver(self.config).strategy

        self.rpc: RPCManager = RPCManager(self)

        self.exchange = ExchangeResolver(self.config['exchange']['name'], self.config).exchange

        self.wallets = Wallets(self.config, self.exchange)
        self.dataprovider = DataProvider(self.config, self.exchange)

        # Attach Dataprovider to Strategy baseclass
        IStrategy.dp = self.dataprovider
        # Attach Wallets to Strategy baseclass
        IStrategy.wallets = self.wallets

        pairlistname = self.config.get('pairlist', {}).get('method', 'StaticPairList')
        self.pairlists = PairListResolver(pairlistname, self, self.config).pairlist

        # Initializing Edge only if enabled
        self.edge = Edge(self.config, self.exchange, self.strategy) if \
            self.config.get('edge', {}).get('enabled', False) else None

        self.active_pair_whitelist: List[str] = self.config['exchange']['pair_whitelist']

        persistence.init(self.config.get('db_url', None),
                         clean_open_orders=self.config.get('dry_run', False))

        # Set initial bot state from config
        initial_state = self.config.get('initial_state')
        self.state = State[initial_state.upper()] if initial_state else State.STOPPED