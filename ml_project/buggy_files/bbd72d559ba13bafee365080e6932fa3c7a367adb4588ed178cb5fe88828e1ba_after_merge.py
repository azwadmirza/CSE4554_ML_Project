    async def on_raw_reaction_remove(self, payload):
        if self.config["transfer_reactions"]:
            await self.handle_reaction_events(payload)