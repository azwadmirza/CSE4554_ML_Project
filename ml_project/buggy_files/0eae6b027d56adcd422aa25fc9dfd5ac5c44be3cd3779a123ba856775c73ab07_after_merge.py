    def open_session(self):
        """Open new channel from session."""
        logger.debug("Opening new channel on %s", self.host)
        try:
            channel = self._open_session()
        except Exception as ex:
            raise SessionError(ex)
        return channel