    def download(self, custom_path=None, out=None, timeout=None):
        """
        Download this file. By default, the file is saved in the current working directory with its
        original filename as reported by Telegram. If a ``custom_path`` is supplied, it will be
        saved to that path instead. If ``out`` is defined, the file contents will be saved to that
        object using the ``out.write`` method. ``custom_path`` and ``out`` are mutually exclusive.

        Args:
            custom_path (Optional[str]): Custom path.
            out (Optional[object]): A file-like object. Must be opened in binary mode, if
                applicable.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Raises:
            ValueError: If both ``custom_path`` and ``out`` are passed.

        """

        if custom_path is not None and out is not None:
            raise ValueError('custom_path and out are mutually exclusive')

        # Convert any UTF-8 char into a url encoded ASCII string.
        sres = urllib_parse.urlsplit(self.file_path)
        url = urllib_parse.urlunsplit(urllib_parse.SplitResult(
            sres.scheme, sres.netloc, urllib_parse.quote(sres.path), sres.query, sres.fragment))

        if out:
            buf = self.bot.request.retrieve(url)
            out.write(buf)

        else:
            if custom_path:
                filename = custom_path
            else:
                filename = basename(self.file_path)

            self.bot.request.download(url, filename, timeout=timeout)