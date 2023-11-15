    async def get_response(self, timeout):
        """Get respoonse with a maximum timeout."""
        await asyncio.wait_for(
            self.semaphore.acquire(), timeout=timeout, loop=self.loop
        )
        return self.result