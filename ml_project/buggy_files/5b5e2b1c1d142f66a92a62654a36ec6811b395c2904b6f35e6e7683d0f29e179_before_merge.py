    def dataReceived(self, data):
        """ 
        Get response, check for valid message, decode result

        :param data: The data returned from the server
        """
        unit = self.framer.decode_data(data).get("uid", 0)
        self.framer.processIncomingPacket(data, self._handleResponse,
                                          unit=unit)