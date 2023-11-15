    def __init__(self, max_wait_time, nthreads=8):
        self.mtime = dict()
        self.mtime_target = PassthroughDict(
            self.mtime
        )  # filled in case of symlink with mtime of target
        self.exists_local = dict()
        self.exists_remote = dict()
        self.size = dict()
        # Indicator whether an inventory has been created for the root of a given IOFile.
        # In case of remote objects the root is the bucket or server host.
        self.has_inventory = set()
        self.remaining_wait_time = max_wait_time
        self.max_wait_time = max_wait_time
        self.queue = queue.Queue()
        self.threads = []
        self.active = False
        self.nthreads = nthreads

        self.activate()