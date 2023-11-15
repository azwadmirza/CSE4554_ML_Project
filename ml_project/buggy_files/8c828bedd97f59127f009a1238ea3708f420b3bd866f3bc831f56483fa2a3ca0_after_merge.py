    async def lock(self, resource: TResource) -> AsyncIterator[None]:
        if resource not in self._locks:
            self._locks[resource] = asyncio.Lock()

        try:
            self._reference_counts[resource] += 1
            async with self._locks[resource]:
                yield
        finally:
            self._reference_counts[resource] -= 1
            if self._reference_counts[resource] <= 0:
                del self._reference_counts[resource]
                del self._locks[resource]