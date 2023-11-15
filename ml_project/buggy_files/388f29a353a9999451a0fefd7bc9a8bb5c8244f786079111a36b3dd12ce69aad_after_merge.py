    async def localblacklist_clear(self, ctx: commands.Context):
        """
        Clears the blacklist.
        """
        await ctx.bot._config.guild(ctx.guild).blacklist.set([])
        await ctx.send(_("Local blacklist has been cleared."))