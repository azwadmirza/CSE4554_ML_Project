    async def close(self) -> None:
        await self._close()
        self._connection = None