    async def content_as_text(self, max_concurrency=1, encoding="UTF-8"):
        """Download the contents of this blob, and decode as text.

        This operation is blocking until all data is downloaded.

        :param int max_concurrency:
            The number of parallel connections with which to download.
        :param str encoding:
            Test encoding to decode the downloaded bytes. Default is UTF-8.
        :rtype: str
        """
        warnings.warn(
            "content_as_text is deprecated, use readall instead",
            DeprecationWarning
        )
        self._max_concurrency = max_concurrency
        self._encoding = encoding
        return await self.readall()