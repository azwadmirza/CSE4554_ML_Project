    async def write(self, data: bytes, timeout: Timeout) -> None:
        if not data:
            return

        try:
            async with self.write_lock:
                self.stream_writer.write(data)
                return await asyncio.wait_for(
                    self.stream_writer.drain(), timeout.write_timeout
                )
        except asyncio.TimeoutError:
            raise WriteTimeout() from None