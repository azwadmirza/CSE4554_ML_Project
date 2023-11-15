    def serve_forever(self, force_event_loop=False, ready=None):
        with self.server_lock:
            self.is_running = True
            self.logger.debug('Webhook Server started.')
            self._ensure_event_loop(force_event_loop=force_event_loop)
            self.loop = IOLoop.current()
            self.http_server.listen(self.port, address=self.listen)

            if ready is not None:
                ready.set()

            self.loop.start()
            self.logger.debug('Webhook Server stopped.')
            self.is_running = False