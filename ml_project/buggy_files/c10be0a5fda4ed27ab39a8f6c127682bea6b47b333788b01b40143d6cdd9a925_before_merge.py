    async def close(self):
        """Close the connection gracefully."""
        if self.is_closed():
            return
        self._mark_stmts_as_closed()
        self._listeners.clear()
        self._log_listeners.clear()
        self._aborted = True
        await self._protocol.close()