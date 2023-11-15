    def perform_files_request(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("torrentinfo?uri=%s" % quote_plus(self.download_uri),
                                         self.on_received_metainfo, capture_errors=False)