    def _read_forward_sock(self, forward_sock, channel):
        while True:
            if channel is None or channel.eof():
                logger.debug("Channel closed, tunnel forward socket reader exiting")
                return
            try:
                data = forward_sock.recv(1024)
            except Exception as ex:
                logger.error("Forward socket read error: %s", ex)
                raise
            data_len = len(data)
            # logger.debug("Read %s data from forward socket", data_len,)
            if data_len == 0:
                sleep(.01)
                continue
            data_written = 0
            while data_written < data_len:
                try:
                    rc, bytes_written = channel.write(data[data_written:])
                except Exception as ex:
                    logger.error("Channel write error: %s", ex)
                    raise
                data_written += bytes_written
                if rc == LIBSSH2_ERROR_EAGAIN:
                    self.poll()
            logger.debug("Wrote all data to channel")