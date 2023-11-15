    async def _perms_blacklist_clear(self, ctx: commands.Context):
        """Clear all keywords added to the blacklist."""
        blacklist = await self.config.guild(ctx.guild).url_keyword_blacklist()
        if not blacklist:
            return await self._embed_msg(ctx, title=_("Nothing in the blacklist."))
        await self.config.guild(ctx.guild).url_keyword_blacklist.clear()
        return await self._embed_msg(
            ctx,
            title=_("Blacklist Modified"),
            description=_("All entries have been removed from the blacklist."),
        )