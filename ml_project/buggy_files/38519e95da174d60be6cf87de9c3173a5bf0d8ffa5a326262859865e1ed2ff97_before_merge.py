    def validate(self, obj, value):
        """
        Validate that the passed in value is a valid memory specification

        It could either be a pure int, when it is taken as a byte value.
        If it has one of the suffixes, it is converted into the appropriate
        pure byte value.
        """
        if isinstance(value, int):
            return value
        num = value[:-1]
        suffix = value[-1]
        if not num.isdigit() and suffix not in ByteSpecification.UNIT_SUFFIXES:
            raise TraitError('{val} is not a valid memory specification. Must be an int or a string with suffix K, M, G, T'.format(val=value))
        else:
            return int(num) * ByteSpecification.UNIT_SUFFIXES[suffix]