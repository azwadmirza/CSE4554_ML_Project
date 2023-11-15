    def append_header(self, name, value):
        """Set or append a header for this response.

        Warning:
            If the header already exists, the new value will be appended
            to it, delimited by a comma. Most header specifications support
            this format, Cookie and Set-Cookie being the notable exceptions.

        Warning:
            For setting cookies, see :py:meth:`~.set_cookie`

        Args:
            name (str): Header name to set (case-insensitive). Must be of
                type ``str`` or ``StringType``, and only character values 0x00
                through 0xFF may be used on platforms that use wide
                characters.
            value (str): Value for the header. Must be of type ``str`` or
                ``StringType``, and only character values 0x00 through 0xFF
                may be used on platforms that use wide characters.

        """
        name = name.lower()
        if name in self._headers:
            value = self._headers[name] + ',' + value

        self._headers[name] = value