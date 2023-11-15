    def _close(self) -> None:
        if self._connection:  # pragma: nobranch
            self._connection.close()
            self.log.debug("Closed connection %s with params: %s", self._connection, self._template)
            self._template.clear()