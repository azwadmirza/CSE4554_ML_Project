    def __init__(self, config: Dict[str, Any], exchange, strategy) -> None:

        self.config = config
        self.exchange = exchange
        self.strategy = strategy

        self.edge_config = self.config.get('edge', {})
        self._cached_pairs: Dict[str, Any] = {}  # Keeps a list of pairs
        self._final_pairs: list = []

        # checking max_open_trades. it should be -1 as with Edge
        # the number of trades is determined by position size
        if self.config['max_open_trades'] != float('inf'):
            logger.critical('max_open_trades should be -1 in config !')

        if self.config['stake_amount'] != constants.UNLIMITED_STAKE_AMOUNT:
            raise OperationalException('Edge works only with unlimited stake amount')

        self._capital_percentage: float = self.edge_config.get('capital_available_percentage')
        self._allowed_risk: float = self.edge_config.get('allowed_risk')
        self._since_number_of_days: int = self.edge_config.get('calculate_since_number_of_days', 14)
        self._last_updated: int = 0  # Timestamp of pairs last updated time
        self._refresh_pairs = True

        self._stoploss_range_min = float(self.edge_config.get('stoploss_range_min', -0.01))
        self._stoploss_range_max = float(self.edge_config.get('stoploss_range_max', -0.05))
        self._stoploss_range_step = float(self.edge_config.get('stoploss_range_step', -0.001))

        # calculating stoploss range
        self._stoploss_range = np.arange(
            self._stoploss_range_min,
            self._stoploss_range_max,
            self._stoploss_range_step
        )

        self._timerange: TimeRange = TimeRange.parse_timerange("%s-" % arrow.now().shift(
            days=-1 * self._since_number_of_days).format('YYYYMMDD'))
        if config.get('fee'):
            self.fee = config['fee']
        else:
            self.fee = self.exchange.get_fee()