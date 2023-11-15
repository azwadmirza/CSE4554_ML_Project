    def decode(self, message):
        """ Wrapper to decode a response packet

        :param message: The raw packet to decode
        :return: The decoded modbus message or None if error
        """
        try:
            return self._helper(message)
        except ModbusException as er:
            _logger.error("Unable to decode response %s" % er)

        except Exception as ex:
            _logger.error(ex)
        return None