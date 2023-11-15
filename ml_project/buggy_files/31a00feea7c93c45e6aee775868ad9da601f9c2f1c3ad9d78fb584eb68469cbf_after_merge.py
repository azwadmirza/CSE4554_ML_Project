    async def _perms_blacklist_delete(self, ctx: commands.Context, *, keyword: str):
        """Removes a keyword from the blacklist."""
        keyword = keyword.lower().strip()
        if not keyword:
            return await ctx.send_help()
        exists = True
        async with self.config.guild(ctx.guild).url_keyword_blacklist() as blacklist:
            if keyword not in blacklist:
                exists = False
            else:
                blacklist.remove(keyword)
        if not exists:
            return await self._embed_msg(ctx, title=_("Keyword is not in the blacklist."))
        else:
            return await self._embed_msg(
                ctx,
                title=_("Blacklist Modified"),
                description=_("Removed: `{blacklisted}` from the blacklist.").format(
                    blacklisted=keyword
                ),
            )