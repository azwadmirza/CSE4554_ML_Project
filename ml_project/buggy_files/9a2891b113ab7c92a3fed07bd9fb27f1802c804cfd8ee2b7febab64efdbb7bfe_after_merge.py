    async def parseloop(self):
        """Parseloop moved out for testing."""
        self.draw_prompt()
        user_input = await self.async_input()
        message = Message(text=user_input, user=self.user, target=None, connector=self)
        await self.opsdroid.parse(message)