    async def blacklist_clear(self, ctx: commands.Context):
        """
        Clears the blacklist.
        """
        await ctx.bot._config.blacklist.set([])
        await ctx.send(_("Blacklist has been cleared."))