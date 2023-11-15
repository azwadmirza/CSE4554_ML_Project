    async def _close_database(self):
        await self.music_cache.run_all_pending_tasks()
        self.music_cache.database.close()