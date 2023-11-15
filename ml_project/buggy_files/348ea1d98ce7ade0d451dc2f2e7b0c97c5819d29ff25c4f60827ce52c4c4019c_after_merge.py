    async def whitelist_clear(self, ctx: commands.Context):
        """
        Clears the whitelist.
        """
        await self.bot._whiteblacklist_cache.clear_whitelist()
        await ctx.send(_("Whitelist has been cleared."))