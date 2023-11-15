    def check_health(self):
        """
        Perform a request to check the health of the torrent that is represented by this widget.
        Don't do this if we are already checking the health or if we have the health info.
        """
        if self.is_health_checking or self.has_health:  # Don't check health again
            return

        self.health_text.setText("checking health...")
        self.set_health_indicator(STATUS_UNKNOWN)
        self.is_health_checking = True
        self.health_request_mgr = TriblerRequestManager()
        self.health_request_mgr.perform_request("torrents/%s/health?timeout=15" % self.torrent_info["infohash"],
                                                self.on_health_response, capture_errors=False)