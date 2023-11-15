    def __init__(self, exchange, pairlistmanager,
                 config: Dict[str, Any], pairlistconfig: Dict[str, Any],
                 pairlist_pos: int) -> None:
        super().__init__(exchange, pairlistmanager, config, pairlistconfig, pairlist_pos)

        if 'stoploss' not in self._config:
            raise OperationalException(
                'PrecisionFilter can only work with stoploss defined. Please add the '
                'stoploss key to your configuration (overwrites eventual strategy settings).')
        self._stoploss = self._config['stoploss']
        self._enabled = self._stoploss != 0

        # Precalculate sanitized stoploss value to avoid recalculation for every pair
        self._stoploss = 1 - abs(self._stoploss)