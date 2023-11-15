    def process_uri_request(self):
        """
        Process a URI request if we have one in the queue.
        """
        if len(self.pending_uri_requests) == 0:
            return

        uri = self.pending_uri_requests.pop()

        # TODO: create a proper confirmation dialog to show results of adding .mdblob files
        # the case for .mdblob files is handled without torrentinfo endpoint
        if uri.startswith('file') and uri.endswith('.mdblob'):
            request_mgr = TriblerRequestManager()
            request_mgr.perform_request("downloads", lambda _: None, method='PUT', data={"uri": uri})
            return

        if uri.startswith('file') or uri.startswith('magnet'):
            self.start_download_from_uri(uri)