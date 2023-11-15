    async def send_pages(
        self, ctx: Context, pages: List[Union[str, discord.Embed]], embed: bool = True
    ):
        """
        Sends pages based on settings.
        """

        if not self.USE_MENU:

            max_pages_in_guild = await ctx.bot.db.help.max_pages_in_guild()
            destination = ctx.author if len(pages) > max_pages_in_guild else ctx

            if embed:
                for page in pages:
                    await destination.send(embed=page)
            else:
                for page in pages:
                    await destination.send(page)
        else:
            await menus.menu(ctx, pages, menus.DEFAULT_CONTROLS)