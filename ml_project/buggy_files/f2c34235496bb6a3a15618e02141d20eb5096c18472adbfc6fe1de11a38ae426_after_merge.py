    async def localwhitelist_clear(self, ctx: commands.Context):
        """
        Clears the whitelist.
        """
        await self.bot._whiteblacklist_cache.clear_whitelist(ctx.guild)
        await ctx.send(_("Local whitelist has been cleared."))