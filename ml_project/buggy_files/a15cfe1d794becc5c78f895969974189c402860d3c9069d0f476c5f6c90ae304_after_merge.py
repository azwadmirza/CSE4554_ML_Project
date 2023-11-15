    def run(self):
        self.running = True

        # Start listening for HTTP requests (and check for shutdown every 0.5 seconds)
        self.server_address = ('127.0.0.1', self.find_free_port())
        self.thumbServer = httpThumbnailServer(self.server_address, httpThumbnailHandler)
        self.thumbServer.daemon_threads = True
        log.info(
            "Starting thumbnail server listening on port %d",
            self.server_address[1])
        self.thumbServer.serve_forever(0.5)