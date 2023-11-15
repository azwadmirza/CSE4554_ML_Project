    def on_request_done(self, result):
        if not result:
            return
        self.requests_done += 1
        if self.requests_done == len(self.pending_requests):
            self.on_requests_done()