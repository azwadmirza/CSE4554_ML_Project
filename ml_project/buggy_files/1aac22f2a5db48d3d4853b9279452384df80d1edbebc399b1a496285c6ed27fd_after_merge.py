    def __init__(self, url="https://pypi.org/", disable_cache=False, fallback=True):
        super(PyPiRepository, self).__init__(url.rstrip("/") + "/simple/")

        self._base_url = url
        self._disable_cache = disable_cache
        self._fallback = fallback

        release_cache_dir = Path(CACHE_DIR) / "cache" / "repositories" / "pypi"
        self._cache = CacheManager(
            {
                "default": "releases",
                "serializer": "json",
                "stores": {
                    "releases": {"driver": "file", "path": str(release_cache_dir)},
                    "packages": {"driver": "dict"},
                },
            }
        )

        self._cache_control_cache = FileCache(str(release_cache_dir / "_http"))
        self._session = CacheControl(session(), cache=self._cache_control_cache)
        self._inspector = Inspector()

        self._name = "PyPI"