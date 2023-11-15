    def set_header(self, name, value):
        """Set a header for this response to a given value.

        Warning:
            Calling this method overwrites the existing value, if any.

        Warning:
            For setting cookies, see instead :meth:`~.set_cookie`

        Args:
            name (str): Header name to set (case-insensitive). Must be of
                type ``str`` or ``StringType``, and only character values 0x00
                through 0xFF may be used on platforms that use wide
                characters.
            value (str): Value for the header. Must be of type ``str`` or
                ``StringType``, and only character values 0x00 through 0xFF
                may be used on platforms that use wide characters.

        """

        # NOTE(kgriffs): normalize name by lowercasing it
        self._headers[name.lower()] = value