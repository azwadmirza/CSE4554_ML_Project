    def error_received(self, exc):
        """Error received during communication."""
        _LOGGER.debug("Error during DNS lookup for %s: %s", self.host, exc)
        self.semaphore.release()