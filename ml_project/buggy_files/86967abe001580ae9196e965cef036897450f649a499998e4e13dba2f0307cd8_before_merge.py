    def get_name_utf8(self):
        """
        Not all names are utf-8, attempt to construct it as utf-8 anyway.
        """
        out = self.get_name()
        try:
            # Try seeing if the delivered encoding is correct and we
            # can convert to utf8 without any issues.
            return out.decode(self.get_encoding()).encode('utf8').decode('utf8')
        except (LookupError, TypeError, ValueError):
            try:
                # The delivered encoding is incorrect, cast it to
                # latin1 and hope for the best (minor corruption).
                return out.decode('latin1').encode('utf8', 'ignore').decode('utf8')
            except (TypeError, ValueError):
                # This is a very nasty string (e.g. u'\u266b'), remove the illegal entries.
                return out.encode('utf8', 'ignore').decode('utf8')