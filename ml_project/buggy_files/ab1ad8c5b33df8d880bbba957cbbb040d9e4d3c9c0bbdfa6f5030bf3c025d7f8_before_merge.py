    def clear(self):
        for req_id, req in list(self.requests_in_flight.items()):
            req.cancel_request()