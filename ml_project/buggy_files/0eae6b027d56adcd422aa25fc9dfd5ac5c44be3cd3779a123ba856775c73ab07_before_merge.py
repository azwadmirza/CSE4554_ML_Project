    def open_session(self):
        """Open new channel from session."""
        logger.debug("Opening new channel on %s", self.host)
        try:
            channel = self.session.channel_new()
            channel.set_blocking(0)
            while channel.open_session() == SSH_AGAIN:
                logger.debug(
                    "Channel open session blocked, waiting on socket..")
                self.poll()
                # Select on open session can dead lock without
                # yielding event loop
                sleep(.1)
        except Exception as ex:
            raise SessionError(ex)
        return channel