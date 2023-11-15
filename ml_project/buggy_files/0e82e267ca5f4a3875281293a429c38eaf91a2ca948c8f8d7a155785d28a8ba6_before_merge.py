    def _read_channel(self, forward_sock, channel):
        while True:
            if channel is None or channel.eof():
                logger.debug("Channel closed, tunnel reader exiting")
                return
            try:
                size, data = channel.read()
            except Exception as ex:
                logger.error("Error reading from channel - %s", ex)
                raise
            # logger.debug("Read %s data from channel" % (size,))
            if size == LIBSSH2_ERROR_EAGAIN:
                self.poll()
                continue
            elif size == 0:
                sleep(.01)
                continue
            try:
                forward_sock.sendall(data)
            except Exception as ex:
                logger.error(
                    "Error sending data to forward socket - %s", ex)
                raise
            logger.debug("Wrote %s data to forward socket", len(data))