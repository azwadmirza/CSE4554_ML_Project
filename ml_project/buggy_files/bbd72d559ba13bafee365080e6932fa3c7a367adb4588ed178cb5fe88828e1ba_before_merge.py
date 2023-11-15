    async def on_raw_reaction_remove(self, payload):
        await self.handle_reaction_events(payload)