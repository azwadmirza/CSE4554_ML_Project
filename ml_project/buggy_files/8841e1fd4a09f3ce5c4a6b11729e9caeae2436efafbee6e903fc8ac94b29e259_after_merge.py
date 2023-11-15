    def append_header(self, name, value):
        """Set or append a header for this response.

        Warning:
            If the header already exists, the new value will be appended
            to it, delimited by a comma. Most header specifications support
            this format, Set-Cookie being the notable exceptions.

        Warning:
            For setting cookies, see :py:meth:`~.set_cookie`

        Args:
            name (str): Header name (case-insensitive). The restrictions
                noted below for the header's value also apply here.
            value (str): Value for the header. Must be of type ``str`` or
                ``StringType`` and contain only US-ASCII characters.
                Under Python 2.x, the ``unicode`` type is also accepted,
                although such strings are also limited to US-ASCII.

        """
        if PY2:
            # NOTE(kgriffs): uwsgi fails with a TypeError if any header
            # is not a str, so do the conversion here. It's actually
            # faster to not do an isinstance check. str() will encode
            # to US-ASCII.
            name = str(name)
            value = str(value)

        name = name.lower()
        if name in self._headers:
            value = self._headers[name] + ',' + value

        self._headers[name] = value