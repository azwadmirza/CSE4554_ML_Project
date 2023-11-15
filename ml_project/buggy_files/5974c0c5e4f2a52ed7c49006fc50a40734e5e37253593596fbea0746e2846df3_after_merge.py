    def schedule_downloads_timer(self, now=False):
        self.downloads_timer = QTimer()
        self.downloads_timer.setSingleShot(True)
        self.downloads_timer.timeout.connect(self.load_downloads)
        self.downloads_timer.start(0 if now else self.REFRESH_INTERVAL_MS)

        self.downloads_timeout_timer = QTimer()
        self.downloads_timeout_timer.setSingleShot(True)
        self.downloads_timeout_timer.timeout.connect(self.on_downloads_request_timeout)
        self.downloads_timeout_timer.start(self.TIMEOUT_INTERVAL_MS)