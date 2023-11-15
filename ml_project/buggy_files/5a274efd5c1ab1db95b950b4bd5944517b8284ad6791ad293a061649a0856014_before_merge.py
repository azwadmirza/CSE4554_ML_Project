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
            return await self._embed_msg(ctx, _("Keyword already in the whitelist."))
        else:
            embed = discord.Embed(title=_("Whitelist modified"), colour=await ctx.embed_colour())
            embed.description = _("Added: `{whitelisted}` to the whitelist.").format(
                whitelisted=keyword
            )
            await ctx.send(embed=embed)