    def _handle_request_error(self, err):
        log.error("An unexpected error occurred creating or sending a request to %s. %s: %s",
                  self.peer, err.type, err.message)
        self.transport.loseConnection()