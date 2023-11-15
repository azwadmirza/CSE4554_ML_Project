    async def parseloop(self):
        """Parseloop moved out for testing."""
        self.draw_prompt()
        user_input = await self.async_input()
        message = Message(user_input, self.user, None, self)
        await self.opsdroid.parse(message)