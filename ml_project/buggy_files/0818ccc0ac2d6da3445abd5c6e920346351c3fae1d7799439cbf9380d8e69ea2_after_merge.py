    async def acquire(self) -> None:
        await self._lock.acquire()