    def clear(self):
        for req in list(self.requests_in_flight.values()):
            req.cancel_request()