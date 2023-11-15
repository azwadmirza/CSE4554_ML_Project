    def get_content(self, strict: bool=True) -> bytes:
        """
        The HTTP message body decoded with the content-encoding header (e.g. gzip)

        Raises:
            ValueError, when the content-encoding is invalid and strict is True.

        See also: :py:class:`raw_content`, :py:attr:`text`
        """
        if self.raw_content is None:
            return None
        ce = self.headers.get("content-encoding")
        if ce:
            try:
                content = encoding.decode(self.raw_content, ce)
                # A client may illegally specify a byte -> str encoding here (e.g. utf8)
                if isinstance(content, str):
                    raise ValueError("Invalid Content-Encoding: {}".format(ce))
                return content
            except ValueError:
                if strict:
                    raise
                return self.raw_content
        else:
            return self.raw_content