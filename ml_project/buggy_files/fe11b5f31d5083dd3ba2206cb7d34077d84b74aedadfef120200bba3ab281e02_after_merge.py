    def __init__(self, *args, **kwargs):
        RawConfigParser.__init__(self, *args, **kwargs)
        self.filename = None
        self.callback = None
        self.lock = RLock()