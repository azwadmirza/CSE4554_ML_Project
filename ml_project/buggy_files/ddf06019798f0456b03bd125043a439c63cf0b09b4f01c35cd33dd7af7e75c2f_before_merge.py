    def _handle_request_error(self, err):
        log.error(
            "An unexpected error occurred creating or sending a request to %s. Error message: %s",
            self.peer, err.getTraceback())
        self.transport.loseConnection()