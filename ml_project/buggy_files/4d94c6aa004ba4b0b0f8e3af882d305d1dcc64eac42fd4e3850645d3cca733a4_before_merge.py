    def connect(self):
        """
        Creates a connection message and calls the socket manager to send it.
        """
        # Initiate the connection
        message = struct.pack('!qii', self._connection_id, self.action, self.transaction_id)
        self.socket_mgr.send_request(message, self)