    def populateResult(self, result):
        """ Populates the modbus result with current frame header

        We basically copy the data back over from the current header
        to the result header. This may not be needed for serial messages.

        :param result: The response packet
        """
        raise NotImplementedException(
            "Method not implemented by derived class")