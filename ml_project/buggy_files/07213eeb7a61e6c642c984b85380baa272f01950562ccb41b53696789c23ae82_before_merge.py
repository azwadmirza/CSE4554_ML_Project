    def _wait_send_receive_lets(self, source, dest, channel, forward_sock):
        try:
            joinall((source, dest), raise_error=True)
        finally:
            logger.debug("Closing channel and forward socket")
            while channel is not None and channel.close() == LIBSSH2_ERROR_EAGAIN:
                self.poll(timeout=.5)
            forward_sock.close()