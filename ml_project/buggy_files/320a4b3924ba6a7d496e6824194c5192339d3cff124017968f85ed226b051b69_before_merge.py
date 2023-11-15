    def text(self):
        """Content of the response, in unicode.

        if Response.encoding is None and chardet module is available, encoding
        will be guessed.
        """

        # Try charset from content-type
        content = None
        encoding = self.encoding

        # Fallback to auto-detected encoding if chardet is available.
        if self.encoding is None:
            encoding = self._detected_encoding()

        # Decode unicode from given encoding.
        try:
            content = str(self.content, encoding, errors='replace')
        except (UnicodeError, TypeError):
            pass

        return content