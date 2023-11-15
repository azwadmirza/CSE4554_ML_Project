    def quote(cls, value):
        """Quote the value for the cookie.  This can be any object supported
        by :attr:`serialization_method`.

        :param value: the value to quote.
        """
        if cls.serialization_method is not None:
            value = cls.serialization_method.dumps(value)
        if cls.quote_base64:
            value = b''.join(
                base64.b64encode(to_bytes(value, "utf8")).splitlines()
            ).strip()
        return value