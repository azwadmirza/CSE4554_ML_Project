    async def get_response(self):
        """Get respoonse with a maximum timeout."""
        await asyncio.wait_for(
            self.semaphore.acquire(), timeout=self.timeout, loop=self.loop
        )
        return self.result