    def on_reload_torrent_info(self, *args):
        """
        This method is called when user clicks the QLabel text showing loading or error message. Here, we reset
        the number of retries to fetch the metainfo. Note color of QLabel is also reset to white.
        """
        self.dialog_widget.loading_files_label.setStyleSheet("color:#ffffff;")
        self.metainfo_retries = 0
        self.perform_files_request()