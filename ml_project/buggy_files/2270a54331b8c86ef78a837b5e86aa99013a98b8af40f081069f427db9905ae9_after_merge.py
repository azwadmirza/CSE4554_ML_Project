    async def _list_alias(self, ctx: commands.Context):
        """List the available aliases on this server."""
        guild_aliases = await self._aliases.get_guild_aliases(ctx.guild)
        if not guild_aliases:
            return await ctx.send(_("There are no aliases on this server."))
        await self.paginate_alias_list(ctx, guild_aliases)