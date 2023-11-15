    async def on_raw_reaction_add(self, payload):
        if self.config["transfer_reactions"]:
            await self.handle_reaction_events(payload)