    def load_downloads(self):
        url = "downloads?get_pieces=1"
        if self.window().download_details_widget.currentIndex() == 3:
            url = "downloads?get_peers=1&get_pieces=1"

        self.downloads_request_mgr.generate_request_id()
        self.downloads_request_mgr.perform_request(url, self.on_received_downloads)