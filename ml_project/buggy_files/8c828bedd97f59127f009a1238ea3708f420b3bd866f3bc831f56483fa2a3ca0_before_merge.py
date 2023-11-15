    def lock(self, resource: Hashable) -> asyncio.Lock:
        if resource not in self._locks:
            self._locks[resource] = asyncio.Lock()
        lock = self._locks[resource]
        return lock