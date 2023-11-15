    def populateResult(self, result):
        """
        Populates the modbus result header

        The serial packets do not have any header information
        that is copied.

        :param result: The response packet
        """
        result.unit_id = self._header['uid']