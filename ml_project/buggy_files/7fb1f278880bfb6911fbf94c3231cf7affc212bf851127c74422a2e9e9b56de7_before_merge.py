    def __init__(self):
        # type: () -> None
        self._registry = cast("DefaultDict[int, Set[str]]", defaultdict(set))
        self._lock = threading.RLock()
        self._getpid = os.getpid
        self._exists = os.path.exists
        self._rmtree = shutil.rmtree
        atexit.register(self.teardown)