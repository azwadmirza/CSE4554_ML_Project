    async def reset(self):
        self._check_open()
        self._listeners.clear()
        self._log_listeners.clear()
        reset_query = self._get_reset_query()
        if reset_query:
            await self.execute(reset_query)