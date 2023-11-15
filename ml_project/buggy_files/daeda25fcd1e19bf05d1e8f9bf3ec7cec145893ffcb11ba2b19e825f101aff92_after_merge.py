    async def _perms_blacklist_add(self, ctx: commands.Context, *, keyword: str):
        """Adds a keyword to the blacklist."""
        keyword = keyword.lower().strip()
        if not keyword:
            return await ctx.send_help()
        exists = False
        async with self.config.guild(ctx.guild).url_keyword_blacklist() as blacklist:
            if keyword in blacklist:
                exists = True
            else:
                blacklist.append(keyword)
        if exists:
            return await self._embed_msg(ctx, title=_("Keyword already in the blacklist."))
        else:
            return await self._embed_msg(
                ctx,
                title=_("Blacklist Modified"),
                description=_("Added: `{blacklisted}` to the blacklist.").format(
                    blacklisted=keyword
                ),
            )