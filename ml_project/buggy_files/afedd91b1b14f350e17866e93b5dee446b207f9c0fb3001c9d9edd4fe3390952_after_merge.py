    def __init__(self, config: Dict[str, Any], validate: bool = True) -> None:
        """
        Initializes this module with the given config,
        it does basic validation whether the specified exchange and pairs are valid.
        :return: None
        """
        self._api: ccxt.Exchange = None
        self._api_async: ccxt_async.Exchange = None

        self._config.update(config)

        # Holds last candle refreshed time of each pair
        self._pairs_last_refresh_time: Dict[Tuple[str, str], int] = {}
        # Timestamp of last markets refresh
        self._last_markets_refresh: int = 0

        # Holds candles
        self._klines: Dict[Tuple[str, str], DataFrame] = {}

        # Holds all open sell orders for dry_run
        self._dry_run_open_orders: Dict[str, Any] = {}

        if config['dry_run']:
            logger.info('Instance is running with dry_run enabled')

        exchange_config = config['exchange']

        # Deep merge ft_has with default ft_has options
        self._ft_has = deep_merge_dicts(self._ft_has, deepcopy(self._ft_has_default))
        if exchange_config.get("_ft_has_params"):
            self._ft_has = deep_merge_dicts(exchange_config.get("_ft_has_params"),
                                            self._ft_has)
            logger.info("Overriding exchange._ft_has with config params, result: %s", self._ft_has)

        # Assign this directly for easy access
        self._ohlcv_candle_limit = self._ft_has['ohlcv_candle_limit']
        self._ohlcv_partial_candle = self._ft_has['ohlcv_partial_candle']

        self._trades_pagination = self._ft_has['trades_pagination']
        self._trades_pagination_arg = self._ft_has['trades_pagination_arg']

        # Initialize ccxt objects
        ccxt_config = self._ccxt_config.copy()
        ccxt_config = deep_merge_dicts(exchange_config.get('ccxt_config', {}),
                                       ccxt_config)
        self._api = self._init_ccxt(
            exchange_config, ccxt_kwargs=ccxt_config)

        ccxt_async_config = self._ccxt_config.copy()
        ccxt_async_config = deep_merge_dicts(exchange_config.get('ccxt_async_config', {}),
                                             ccxt_async_config)
        self._api_async = self._init_ccxt(
            exchange_config, ccxt_async, ccxt_kwargs=ccxt_async_config)

        logger.info('Using Exchange "%s"', self.name)

        if validate:
            # Check if timeframe is available
            self.validate_timeframes(config.get('ticker_interval'))

            # Initial markets load
            self._load_markets()

            # Check if all pairs are available
            self.validate_stakecurrency(config['stake_currency'])
            self.validate_pairs(config['exchange']['pair_whitelist'])
            self.validate_ordertypes(config.get('order_types', {}))
            self.validate_order_time_in_force(config.get('order_time_in_force', {}))
            self.validate_required_startup_candles(config.get('startup_candle_count', 0))

        # Converts the interval provided in minutes in config to seconds
        self.markets_refresh_interval: int = exchange_config.get(
            "markets_refresh_interval", 60) * 60