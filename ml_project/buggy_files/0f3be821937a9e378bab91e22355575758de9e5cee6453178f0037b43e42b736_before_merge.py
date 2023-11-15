    def __init__(self, out_dir, **kwargs):
        super().__init__(out_dir, **kwargs)
        self.data_paths = []
        self.data_writers = []
        self.data_bios = []
        self._lock = threading.RLock()
        self.pwriter = self._pwriter
        self.pwriter_kwargs = {}