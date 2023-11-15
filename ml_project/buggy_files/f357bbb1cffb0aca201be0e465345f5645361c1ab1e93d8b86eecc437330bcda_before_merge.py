    def shutdown(self):
        with self.shutdown_lock:
            if not self.is_running:
                self.logger.warn('Webhook Server already stopped.')
                return
            else:
                super(WebhookServer, self).shutdown()
                self.is_running = False