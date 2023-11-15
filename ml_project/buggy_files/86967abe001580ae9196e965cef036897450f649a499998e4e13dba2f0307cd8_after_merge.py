    def get_name_utf8(self):
        """
        Not all names are utf-8, attempt to construct it as utf-8 anyway.
        """
        return escape_as_utf8(self.get_name(), self.get_encoding())