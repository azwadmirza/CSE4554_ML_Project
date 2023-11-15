    def __init__(self, max_size=1000):
        """Initialize the cache with a maximum size."""
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = Lock()