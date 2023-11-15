    async def whitelist_clear(self, ctx: commands.Context):
        """
        Clears the whitelist.
        """
        await ctx.bot._config.whitelist.set([])
        await ctx.send(_("Whitelist has been cleared."))