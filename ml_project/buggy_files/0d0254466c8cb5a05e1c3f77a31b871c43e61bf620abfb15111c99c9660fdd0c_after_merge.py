    def buildPacket(self, message):
        """ Creates a ready to send modbus packet

        The raw packet is built off of a fully populated modbus
        request / response message.

        :param message: The request/response to send
        :returns: The built packet
        """
        raise NotImplementedException(
            "Method not implemented by derived class")