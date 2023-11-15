    def send(self, data):
        """Send data to client, return any unsent data."""
        try:
            sent = self.sock.send(data)
            return data[sent:]
        except socket.error as e:
            if e.errno in (errno.EWOULDBLOCK, errno.EINTR):
                return data
            self.stop(
                'Unexpected client error: %s' % encoding.locale_decode(e))
            return b''