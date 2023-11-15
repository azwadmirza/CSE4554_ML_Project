    def single_string(self):
        """Creates a long string with the ascii art.
        Returns:
            str: The lines joined by a newline (``\\n``)
        """
        try:
            return "\n".join(self.lines()).encode(self.encoding).decode(self.encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            warn('The encoding %s has a limited charset. Consider a different encoding in your '
                 'environment. UTF-8 is being used instead' % self.encoding, RuntimeWarning)
            self.encoding = 'utf-8'
            return "\n".join(self.lines()).encode(self.encoding).decode(self.encoding)