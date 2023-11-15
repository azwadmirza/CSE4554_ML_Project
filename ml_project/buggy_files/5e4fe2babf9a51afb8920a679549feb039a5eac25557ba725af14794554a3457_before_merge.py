    async def run_tasks(self, ctx: Optional[commands.Context] = None, _id=None):
        lock_id = _id or ctx.message.id
        lock_author = ctx.author if ctx else None
        async with self._lock:
            if lock_id in self._tasks:
                log.debug(f"Running database writes for {lock_id} ({lock_author})")
                with contextlib.suppress(Exception):
                    tasks = self._tasks[ctx.message.id]
                    del self._tasks[ctx.message.id]
                    await asyncio.gather(
                        *[self.insert(*a) for a in tasks["insert"]], return_exceptions=True
                    )
                    await asyncio.gather(
                        *[self.update(*a) for a in tasks["update"]], return_exceptions=True
                    )
                log.debug(f"Completed database writes for {lock_id} " f"({lock_author})")