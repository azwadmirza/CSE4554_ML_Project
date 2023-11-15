    async def create_connection(self, with_db: bool) -> None:
        await self._parent.create_connection(with_db)
        self._connection = self._parent._connection