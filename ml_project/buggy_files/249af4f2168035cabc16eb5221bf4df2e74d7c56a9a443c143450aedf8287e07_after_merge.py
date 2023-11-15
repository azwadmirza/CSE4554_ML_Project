    def load_downloads(self):
        url = "downloads?get_pieces=1"
        if self.window().download_details_widget.currentIndex() == 3:
            url = "downloads?get_peers=1&get_pieces=1"

        if not self.isHidden() or (time.time() - self.downloads_last_update > 30):
            # Update if the downloads page is visible or if we haven't updated for longer than 30 seconds
            self.downloads_last_update = time.time()
            priority = "LOW" if self.isHidden() else "HIGH"
            self.downloads_request_mgr.cancel_request()
            self.downloads_request_mgr = TriblerRequestManager()
            self.downloads_request_mgr.perform_request(url, self.on_received_downloads, priority=priority)