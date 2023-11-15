    async def _clear_react(self, message: discord.Message, emoji: dict = None):
        """Non blocking version of clear_react"""
        return self.bot.loop.create_task(clear_react(self.bot, message, emoji))