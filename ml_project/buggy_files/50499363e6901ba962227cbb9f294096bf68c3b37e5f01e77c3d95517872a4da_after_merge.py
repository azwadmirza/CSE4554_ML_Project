    async def sendfile(self, writer: asyncio.StreamWriter) -> int:
        """
        Read and send the file to the writer and return the number of bytes sent
        """

        if not self.is_readable():
            raise OSError('blob files cannot be read')
        with self.reader_context() as handle:
            try:
                return await self.loop.sendfile(writer.transport, handle, count=self.get_length())
            except (ConnectionError, BrokenPipeError, RuntimeError, OSError, AttributeError):
                return -1