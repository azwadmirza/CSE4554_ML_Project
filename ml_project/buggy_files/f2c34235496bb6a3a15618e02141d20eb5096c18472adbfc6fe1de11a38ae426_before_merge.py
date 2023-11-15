    async def localwhitelist_clear(self, ctx: commands.Context):
        """
        Clears the whitelist.
        """
        await ctx.bot._config.guild(ctx.guild).whitelist.set([])
        await ctx.send(_("Whitelist has been cleared."))