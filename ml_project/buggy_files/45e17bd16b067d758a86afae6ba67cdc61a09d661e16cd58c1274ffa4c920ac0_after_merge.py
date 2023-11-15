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

        # NOTE(kgriffs): normalize name by lowercasing it
        self._headers[name.lower()] = value