    def dataReceived(self, data):
        """
        Handle non-AMP messages, such as HTTP communication.
        """
        if data[0] != b'\0':
            self.transport.write(_HTTP_WARNING)
            self.transport.loseConnection()
        else:
            super(AMPMultiConnectionProtocol, self).dataReceived(data)