    def evict_timed_out_requests(self):
        t = time()
        for req in self.requests_in_flight:
            if t - req.time > self.request_timeout_interval:
                req.cancel_request()