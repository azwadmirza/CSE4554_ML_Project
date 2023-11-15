    def __init__(self, dist):
        self.paths = set()
        self._refuse = set()
        self.pth = {}
        self.dist = dist
        self.save_dir = TempDirectory(kind="uninstall")
        self._moved_paths = []