    def serve_forever(self):
        with self.server_lock:
            IOLoop().make_current()
            self.is_running = True
            self.logger.debug('Webhook Server started.')
            self.http_server.listen(self.port, address=self.listen)
            self.loop = IOLoop.current()
            self.loop.start()
            self.logger.debug('Webhook Server stopped.')
            self.is_running = False