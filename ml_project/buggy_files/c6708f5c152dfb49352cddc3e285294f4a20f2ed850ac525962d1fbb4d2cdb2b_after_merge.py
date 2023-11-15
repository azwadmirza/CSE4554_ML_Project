    def fromRegisters(klass, registers, endian=Endian.Little):
        ''' Initialize a payload decoder with the result of
        reading a collection of registers from a modbus device.

        The registers are treated as a list of 2 byte values.
        We have to do this because of how the data has already
        been decoded by the rest of the library.

        :param registers: The register results to initialize with
        :param endian: The endianess of the payload
        :returns: An initialized PayloadDecoder
        '''
        if isinstance(registers, list):  # repack into flat binary
            payload = b''.join(pack('!H', x) for x in registers)
            return klass(payload, endian)
        raise ParameterException('Invalid collection of registers supplied')