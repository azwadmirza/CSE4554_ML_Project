    async def save(self, fp, *, seek_begin=True, use_cached=True):
        """|coro|

        Saves this attachment into a file-like object.

        Parameters
        -----------
        fp: Union[BinaryIO, str]
            The file-like object to save this attachment to or the filename
            to use. If a filename is passed then a file is created with that
            filename and used instead.
        seek_begin: :class:`bool`
            Whether to seek to the beginning of the file after saving is
            successfully done.
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, which is generally deleted right after the message is deleted.
            Note that this can still fail to download deleted attachments if too much time
            has passed.

        Raises
        --------
        HTTPException
            Saving the attachment failed.
        NotFound
            The attachment was deleted.

        Returns
        --------
        int
            The number of bytes written.
        """
        url = self.proxy_url if use_cached else self.url
        data = await self._http.get_attachment(url)
        if isinstance(fp, str):
            with open(fp, 'wb') as f:
                return f.write(data)
        else:
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written