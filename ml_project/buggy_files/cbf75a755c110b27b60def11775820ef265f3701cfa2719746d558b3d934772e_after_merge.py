    async def run_all_pending_tasks(self):
        async with self._lock:
            log.debug("Running pending writes to database")
            with contextlib.suppress(Exception):
                tasks = {"update": [], "insert": []}
                for (k, task) in self._tasks.items():
                    for t, args in task.items():
                        tasks[t].append(args)
                self._tasks = {}

                await asyncio.gather(
                    *[self.database.insert(*a) for a in tasks["insert"]], return_exceptions=True
                )
                await asyncio.gather(
                    *[self.database.update(*a) for a in tasks["update"]], return_exceptions=True
                )
            log.debug("Completed pending writes to database have finished")