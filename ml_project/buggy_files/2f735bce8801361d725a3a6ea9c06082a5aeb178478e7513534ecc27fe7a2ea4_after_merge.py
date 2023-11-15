    def __init__(self, config: Config):
        self._config: Config = config
        self._cached_whitelist: Dict[Optional[int], List[int]] = {}
        self._cached_blacklist: Dict[Optional[int], List[int]] = {}