    async def async_set_shuffle(self, shuffle):
        """Enable/disable shuffle mode."""
        self.check_login_changes()
        await self.alexa_api.shuffle(shuffle)
        self._shuffle = shuffle