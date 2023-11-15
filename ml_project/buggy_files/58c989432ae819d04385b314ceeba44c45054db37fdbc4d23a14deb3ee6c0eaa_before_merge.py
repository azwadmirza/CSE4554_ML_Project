    async def async_set_shuffle(self, shuffle):
        """Enable/disable shuffle mode."""
        await self.alexa_api.shuffle(shuffle)
        self._shuffle = shuffle