    def __init__(
        self,
        build_requests,
        install_requests,
        package_index_configuration=None,
        cache=None,
        compile=False,
    ):

        self._build_requests = build_requests
        self._install_requests = install_requests
        self._package_index_configuration = package_index_configuration
        self._cache = cache
        self._compile = compile