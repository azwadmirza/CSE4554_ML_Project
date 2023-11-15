    async def close(self) -> None:
        self._close()
        self._connection = None