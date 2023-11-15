    async def _perms_blacklist_list(self, ctx: commands.Context):
        """List all keywords added to the blacklist."""
        blacklist = await self.config.guild(ctx.guild).url_keyword_blacklist()
        if not blacklist:
            return await self._embed_msg(ctx, title=_("Nothing in the blacklist."))
        blacklist.sort()
        text = ""
        total = len(blacklist)
        pages = []
        for i, entry in enumerate(blacklist, 1):
            text += f"{i}. [{entry}]"
            if i != total:
                text += "\n"
                if i % 10 == 0:
                    pages.append(box(text, lang="ini"))
                    text = ""
            else:
                pages.append(box(text, lang="ini"))
        embed_colour = await ctx.embed_colour()
        pages = list(
            discord.Embed(title="Blacklist", description=page, colour=embed_colour)
            for page in pages
        )
        await menu(ctx, pages, DEFAULT_CONTROLS)