    async def listen(self):
        """Listen for and parse new messages.

        The bot will always listen to all opened chat windows,
        as long as opsdroid is running. Since anyone can start
        a new chat with the bot is recommended that a list of
        users to be whitelisted be provided in config.yaml.

        The method will sleep asynchronously at the end of
        every loop. The time can either be specified in the
        config.yaml with the param update-interval - this
        defaults to 1 second.

        Args:
            opsdroid (OpsDroid): An instance of opsdroid core.

        """
        while self.listening:
            await self._get_messages()

            await asyncio.sleep(self.update_interval)