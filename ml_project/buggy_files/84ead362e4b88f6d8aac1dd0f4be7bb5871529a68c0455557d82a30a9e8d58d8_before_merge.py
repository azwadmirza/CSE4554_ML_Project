    def __init__(self, d: StoredDict):
        super().__init__(d)
        self.force_watching_only = False
        self.ux_busy = False