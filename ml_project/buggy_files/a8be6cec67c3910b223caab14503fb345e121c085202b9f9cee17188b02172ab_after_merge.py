    def __init__(self, lockfile, friendly=False, **kwargs):
        self._friendly = friendly
        self.lockfile = lockfile
        self._lock = None