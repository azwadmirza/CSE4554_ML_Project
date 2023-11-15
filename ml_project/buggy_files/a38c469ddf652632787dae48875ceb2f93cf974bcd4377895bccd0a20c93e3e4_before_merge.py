    def __init__(self, dirpath=None):
        self.process = Process()
        self._is_windows = sys.platform == "win32"
        self._bin_extension = ".exe" if self._is_windows else ""
        self.settings = settings.VirtualEnvironmentSettings()
        self.settings.init()
        self.relocate(dirpath or self.settings["dirpath"])