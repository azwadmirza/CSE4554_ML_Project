    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.subscribe_button = None
        self.channel_info = None
        self.num_subs_label = None
        self.request_mgr = None
        self.initialized = False