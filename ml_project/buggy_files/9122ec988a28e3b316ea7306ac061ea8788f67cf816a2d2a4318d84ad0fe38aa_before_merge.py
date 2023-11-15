    def _validate_unit_id(self, units, single):
        """
        Validates if the received data is valid for the client
        :param units: list of unit id for which the transaction is valid
        :param single: Set to true to treat this as a single context
        :return:         """

        if single:
            return True
        else:
            if 0 in units or 0xFF in units:
                # Handle Modbus TCP unit identifier (0x00 0r 0xFF)
                # in async requests
                return True
            return self._header['uid'] in units