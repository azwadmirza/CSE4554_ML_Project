    async def _close(self) -> None:
        await self._parent._close()
        self._connection = self._parent._connection