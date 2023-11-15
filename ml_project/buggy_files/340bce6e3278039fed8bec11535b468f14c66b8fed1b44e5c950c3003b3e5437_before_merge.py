    def fromCoils(klass, coils, byteorder=Endian.Little):
        """ Initialize a payload decoder with the result of
        reading a collection of coils from a modbus device.

        The coils are treated as a list of bit(boolean) values.

        :param coils: The coil results to initialize with
        :param byteorder: The endianess of the payload
        :returns: An initialized PayloadDecoder
        """
        if isinstance(coils, list):
            payload = pack_bitstring(coils)
            return klass(payload, byteorder)
        raise ParameterException('Invalid collection of coils supplied')