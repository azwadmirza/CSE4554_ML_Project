    def evict_timed_out_requests(self):
        t = time()
        for req in list(self.requests_in_flight.values()):
            if t - req.time > self.request_timeout_interval:
                req.cancel_request()