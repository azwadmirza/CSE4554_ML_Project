    def decode(self, message):
        ''' Wrapper to decode a given packet

        :param message: The raw modbus request packet
        :return: The decoded modbus message or None if error
        '''
        raise NotImplementedException(
            "Method not implemented by derived class")