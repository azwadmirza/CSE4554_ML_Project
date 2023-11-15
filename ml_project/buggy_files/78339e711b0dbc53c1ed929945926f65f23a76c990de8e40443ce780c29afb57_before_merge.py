    async def on_raw_reaction_add(self, payload):
        await self.handle_reaction_events(payload)