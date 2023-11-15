    def __init__(self):
        QWidget.__init__(self)
        self.export_dir = None
        self.filter = DOWNLOADS_FILTER_ALL
        self.download_widgets = {}  # key: infohash, value: QTreeWidgetItem
        self.downloads = None
        self.downloads_timer = QTimer()
        self.downloads_timeout_timer = QTimer()
        self.downloads_last_update = 0
        self.selected_item = None
        self.dialog = None
        self.downloads_request_mgr = TriblerRequestManager()
        self.request_mgr = None