    def load_downloads(self):
        url = "downloads?get_pieces=1"
        if time.time() - self.downloads_last_update > 30:
            self.downloads_last_update = time.time()
            self.downloads_request_mgr.cancel_request()
            self.downloads_request_mgr = TriblerRequestManager()
            self.downloads_request_mgr.perform_request(url, self.on_received_downloads, priority="LOW")