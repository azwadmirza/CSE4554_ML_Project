    def decode(self, message):
        ''' Wrapper to decode a request packet

        :param message: The raw modbus request packet
        :return: The decoded modbus message or None if error
        '''
        try:
            return self._helper(message)
        except ModbusException as er:
            _logger.warning("Unable to decode request %s" % er)
        return None