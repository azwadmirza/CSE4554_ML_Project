    def set_header(self, name, value):
        """Set a header for this response to a given value.

        Warning:
            Calling this method overwrites the existing value, if any.

        Warning:
            For setting cookies, see instead :meth:`~.set_cookie`

        Args:
            name (str): Header name (case-insensitive). The restrictions
                noted below for the header's value also apply here.
            value (str): Value for the header. Must be of type ``str`` or
                ``StringType`` and contain only ISO-8859-1 characters.
                Under Python 2.x, the ``unicode`` type is also accepted,
                although such strings are also limited to ISO-8859-1.
        """
        name, value = self._encode_header(name, value)

        # NOTE(kgriffs): normalize name by lowercasing it
        self._headers[name.lower()] = value