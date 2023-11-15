    def __init__(self):
        QWidget.__init__(self)
        self.trust_plot = None
        self.public_key = None
        self.request_mgr = None
        self.statistics = None
        self.blocks = None
        self.byte_scale = 1024 * 1024
        self.refresh_timer = None