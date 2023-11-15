    def set_headers(self, headers):
        """Set several headers at once.

        Warning:
            Calling this method overwrites existing values, if any.

        Args:
            headers (dict or list): A dictionary of header names and values
                to set, or a ``list`` of (*name*, *value*) tuples. Both *name*
                and *value* must be of type ``str`` or ``StringType`` and
                contain only US-ASCII characters. Under Python 2.x, the
                ``unicode`` type is also accepted, although such strings are
                also limited to US-ASCII.

                Note:
                    Falcon can process a list of tuples slightly faster
                    than a dict.

        Raises:
            ValueError: `headers` was not a ``dict`` or ``list`` of ``tuple``.

        """

        if isinstance(headers, dict):
            headers = headers.items()

        # NOTE(kgriffs): We can't use dict.update because we have to
        # normalize the header names.
        _headers = self._headers

        if PY2:
            for name, value in headers:
                # NOTE(kgriffs): uwsgi fails with a TypeError if any header
                # is not a str, so do the conversion here. It's actually
                # faster to not do an isinstance check. str() will encode
                # to US-ASCII.
                name = str(name)
                value = str(value)

                _headers[name.lower()] = value

        else:
            for name, value in headers:
                _headers[name.lower()] = value