    async def _perms_whitelist_add(self, ctx: commands.Context, *, keyword: str):
        """Adds a keyword to the whitelist.

        If anything is added to whitelist, it will blacklist everything else.
        """
        keyword = keyword.lower().strip()
        if not keyword:
            return await ctx.send_help()
        exists = False
        async with self.config.guild(ctx.guild).url_keyword_whitelist() as whitelist:
            if keyword in whitelist:
                exists = True
            else:
                whitelist.append(keyword)
        if exists:
            return await self._embed_msg(ctx, title=_("Keyword already in the whitelist."))
        else:
            return await self._embed_msg(
                ctx,
                title=_("Whitelist Modified"),
                description=_("Added: `{whitelisted}` to the whitelist.").format(
                    whitelisted=keyword
                ),
            )