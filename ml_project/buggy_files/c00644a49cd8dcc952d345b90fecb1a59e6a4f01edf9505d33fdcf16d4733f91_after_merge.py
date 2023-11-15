    def __init__(self):
        QWidget.__init__(self)

        self.channel_identifier = None
        self.request_mgr = None
        self.dialog = None
        self.selected_item_index = -1
        self.initialized = False