    async def blacklist_clear(self, ctx: commands.Context):
        """
        Clears the blacklist.
        """
        await self.bot._whiteblacklist_cache.clear_blacklist()
        await ctx.send(_("Blacklist has been cleared."))