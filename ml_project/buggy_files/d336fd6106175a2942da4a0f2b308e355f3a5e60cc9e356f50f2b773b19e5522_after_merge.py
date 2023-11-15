    async def _perms_whitelist_clear(self, ctx: commands.Context):
        """Clear all keywords from the whitelist."""
        whitelist = await self.config.guild(ctx.guild).url_keyword_whitelist()
        if not whitelist:
            return await self._embed_msg(ctx, title=_("Nothing in the whitelist."))
        await self.config.guild(ctx.guild).url_keyword_whitelist.clear()
        return await self._embed_msg(
            ctx,
            title=_("Whitelist Modified"),
            description=_("All entries have been removed from the whitelist."),
        )