    def __init__(self, exchange, pairlistmanager,
                 config: Dict[str, Any], pairlistconfig: Dict[str, Any],
                 pairlist_pos: int) -> None:
        """
        :param exchange: Exchange instance
        :param pairlistmanager: Instanciating Pairlist manager
        :param config: Global bot configuration
        :param pairlistconfig: Configuration for this pairlist - can be empty.
        :param pairlist_pos: Position of the filter in the pairlist-filter-list
        """
        self._exchange = exchange
        self._pairlistmanager = pairlistmanager
        self._config = config
        self._pairlistconfig = pairlistconfig
        self._pairlist_pos = pairlist_pos