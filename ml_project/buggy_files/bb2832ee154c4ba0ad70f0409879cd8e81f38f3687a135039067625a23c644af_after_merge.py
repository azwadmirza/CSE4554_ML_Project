    def redirect(self, location, status=302, lock=0):
        """Cause a redirection without raising an error"""
        if isinstance(location, HTTPRedirection):
            status = location.getStatus()
            location = location.headers['Location']

        if PY2 and isinstance(location, text_type):
            location = location.encode(self.charset)
        elif PY3 and isinstance(location, binary_type):
            location = location.decode(self.charset)

        # To be entirely correct, we must make sure that all non-ASCII
        # characters in the path part are quoted correctly. This is required
        # as we now allow non-ASCII IDs
        parsed = list(urlparse(location))
        parsed[2] = quote(parsed[2])
        location = urlunparse(parsed)

        self.setStatus(status, lock=lock)
        self.setHeader('Location', location)
        return location