    def _wait_send_receive_lets(self, source, dest, channel, forward_sock):
        try:
            joinall((source, dest), raise_error=True)
        finally:
            logger.debug("Closing channel and forward socket")
            self._client.close_channel(channel)
            forward_sock.close()