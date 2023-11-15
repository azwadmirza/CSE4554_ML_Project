    def __init__(self, dirpath=None):
        self.process = Process()
        self._is_windows = sys.platform == "win32"
        self._bin_extension = ".exe" if self._is_windows else ""
        self.settings = settings.VirtualEnvironmentSettings()
        self.settings.init()
        dirpath_to_use = (
            dirpath or self.settings.get("dirpath") or self._generate_dirpath()
        )
        logger.info("Using dirpath: %s", dirpath_to_use)
        self.relocate(dirpath_to_use)