    async def _perms_whitelist_list(self, ctx: commands.Context):
        """List all keywords added to the whitelist."""
        whitelist = await self.config.guild(ctx.guild).url_keyword_whitelist()
        if not whitelist:
            return await self._embed_msg(ctx, title=_("Nothing in the whitelist."))
        whitelist.sort()
        text = ""
        total = len(whitelist)
        pages = []
        for i, entry in enumerate(whitelist, 1):
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
            discord.Embed(title="Whitelist", description=page, colour=embed_colour)
            for page in pages
        )
        await menu(ctx, pages, DEFAULT_CONTROLS)