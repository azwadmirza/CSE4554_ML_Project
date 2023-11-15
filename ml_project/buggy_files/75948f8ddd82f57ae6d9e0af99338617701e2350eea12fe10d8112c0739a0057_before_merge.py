    def __init__(
        self,
        build_requests,
        install_requests,
        indexes=None,
        find_links=None,
        network_configuration=None,
        cache=None,
        compile=False,
    ):

        self._build_requests = build_requests
        self._install_requests = install_requests
        self._indexes = indexes
        self._find_links = find_links
        self._network_configuration = network_configuration
        self._cache = cache
        self._compile = compile