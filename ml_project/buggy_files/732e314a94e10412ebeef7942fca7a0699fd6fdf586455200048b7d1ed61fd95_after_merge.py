    async def multiglob(self, *patterns, folder=False) -> AsyncIterator["LocalPath"]:
        async for p in AsyncIter(patterns):
            async for path in self._multiglob(p, folder, self.glob):
                yield path