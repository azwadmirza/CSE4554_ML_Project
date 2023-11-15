    def __init__(self):
        # type: () -> None
        self._registry = defaultdict(set)  # type: DefaultDict[int, Set[str]]
        self._lock = threading.RLock()
        self._getpid = os.getpid
        self._exists = os.path.exists
        self._rmtree = shutil.rmtree
        atexit.register(self.teardown)