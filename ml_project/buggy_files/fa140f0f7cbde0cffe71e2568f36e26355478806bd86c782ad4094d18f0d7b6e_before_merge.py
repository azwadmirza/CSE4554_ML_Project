    async def _perms_whitelist_delete(self, ctx: commands.Context, *, keyword: str):
        """Removes a keyword from the whitelist."""
        keyword = keyword.lower().strip()
        if not keyword:
            return await ctx.send_help()
        exists = True
        async with self.config.guild(ctx.guild).url_keyword_whitelist() as whitelist:
            if keyword not in whitelist:
                exists = False
            else:
                whitelist.remove(keyword)
        if not exists:
            return await self._embed_msg(ctx, _("Keyword already in the whitelist."))
        else:
            embed = discord.Embed(title=_("Whitelist modified"), colour=await ctx.embed_colour())
            embed.description = _("Removed: `{whitelisted}` from the whitelist.").format(
                whitelisted=keyword
            )
            await ctx.send(embed=embed)