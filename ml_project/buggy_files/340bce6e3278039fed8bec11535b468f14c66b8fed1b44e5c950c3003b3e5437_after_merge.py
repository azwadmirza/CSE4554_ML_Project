    def fromCoils(klass, coils, byteorder=Endian.Little, wordorder=Endian.Big):
        """ Initialize a payload decoder with the result of
        reading a collection of coils from a modbus device.

        The coils are treated as a list of bit(boolean) values.

        :param coils: The coil results to initialize with
        :param byteorder: The endianess of the payload
        :returns: An initialized PayloadDecoder
        """
        if isinstance(coils, list):
            payload = b''
            padding = len(coils) % 8
            if padding:    # Pad zero's
                extra = [False] * padding
                coils = extra + coils
            chunks = klass.bit_chunks(coils)
            for chunk in chunks:
                payload += pack_bitstring(chunk[::-1])
            return klass(payload, byteorder)
        raise ParameterException('Invalid collection of coils supplied')