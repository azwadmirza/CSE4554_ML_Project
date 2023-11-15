    async def multirglob(self, *patterns, folder=False) -> AsyncIterator["LocalPath"]:
        for p in patterns:
            for rp in self.rglob(p):
                rp = LocalPath(rp)
                if folder and rp.is_dir() and rp.exists():
                    yield rp
                    await asyncio.sleep(0)
                else:
                    if rp.suffix in self._all_music_ext and rp.is_file() and rp.exists():
                        yield rp
                        await asyncio.sleep(0)