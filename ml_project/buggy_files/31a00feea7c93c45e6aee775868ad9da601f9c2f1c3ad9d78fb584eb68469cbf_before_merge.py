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
            return await self._embed_msg(ctx, _("Keyword is not in the blacklist."))
        else:
            embed = discord.Embed(title=_("Blacklist modified"), colour=await ctx.embed_colour())
            embed.description = _("Removed: `{blacklisted}` from the blacklist.").format(
                blacklisted=keyword
            )
            await ctx.send(embed=embed)