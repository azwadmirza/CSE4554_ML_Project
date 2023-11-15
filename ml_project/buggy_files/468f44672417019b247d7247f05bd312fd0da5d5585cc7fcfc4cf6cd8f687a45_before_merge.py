    def __init__(self, oid, value):
        if not isinstance(oid, ObjectIdentifier):
            raise TypeError(
                "oid argument must be an ObjectIdentifier instance."
            )

        if not isinstance(value, six.text_type):
            raise TypeError(
                "value argument must be a text type."
            )

        if oid == NameOID.COUNTRY_NAME and len(value.encode("utf8")) != 2:
            raise ValueError(
                "Country name must be a 2 character country code"
            )

        self._oid = oid
        self._value = value