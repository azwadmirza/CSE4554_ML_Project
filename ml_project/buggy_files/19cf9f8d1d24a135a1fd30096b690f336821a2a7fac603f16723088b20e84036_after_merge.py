    async def close(self) -> None:
        async with self.write_lock:
            await self.stream.aclose()