    async def send_pages(
        self, ctx: Context, pages: List[Union[str, discord.Embed]], embed: bool = True
    ):
        """
        Sends pages based on settings.
        """

        if not (
            ctx.channel.permissions_for(ctx.me).add_reactions and await ctx.bot.db.help.use_menus()
        ):

            max_pages_in_guild = await ctx.bot.db.help.max_pages_in_guild()
            destination = ctx.author if len(pages) > max_pages_in_guild else ctx

            if embed:
                for page in pages:
                    try:
                        await destination.send(embed=page)
                    except discord.Forbidden:
                        await ctx.send(
                            T_(
                                "I couldn't send the help message to you in DM. "
                                "Either you blocked me or you disabled DMs in this server."
                            )
                        )
            else:
                for page in pages:
                    try:
                        await destination.send(page)
                    except discord.Forbidden:
                        await ctx.send(
                            T_(
                                "I couldn't send the help message to you in DM. "
                                "Either you blocked me or you disabled DMs in this server."
                            )
                        )
        else:
            if len(pages) > 1:
                await menus.menu(ctx, pages, menus.DEFAULT_CONTROLS)
            else:
                await menus.menu(ctx, pages, {"\N{CROSS MARK}": menus.close_menu})