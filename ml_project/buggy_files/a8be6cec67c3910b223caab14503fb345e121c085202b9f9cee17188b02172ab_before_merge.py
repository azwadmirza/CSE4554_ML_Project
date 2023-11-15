        def __init__(self, lockfile, tmp_dir=None):
            self.lockfile = lockfile
            self._lock = None