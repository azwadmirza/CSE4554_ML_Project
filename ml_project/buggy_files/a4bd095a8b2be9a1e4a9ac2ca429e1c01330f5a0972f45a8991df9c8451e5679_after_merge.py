    def __init__(self, parent):
        QListWidget.__init__(self, parent)

        self.files_data = []
        self.loaded_list = False
        self.loading_list = False
        self.active_index = -1
        self.infohash = None
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.files_request_mgr = None
        self.files_request_timer = None