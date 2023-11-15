    async def close(self) -> None:
        await self.stream.aclose()