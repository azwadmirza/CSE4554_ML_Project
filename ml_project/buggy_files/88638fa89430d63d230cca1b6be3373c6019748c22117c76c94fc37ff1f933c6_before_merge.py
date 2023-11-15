    async def _game(self, ctx: commands.Context, *, game: str = None):
        """Sets [botname]'s playing status"""

        if len(game) > 128:
            await ctx.send("The maximum length of game descriptions is 128 characters.")
        else:
            if game:
                game = discord.Game(name=game)
            else:
                game = None
            status = (
                ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else discord.Status.online
            )
            await ctx.bot.change_presence(status=status, activity=game)
            if game:
                await ctx.send(_("Status set to ``Playing {game.name}``.").format(game=game))
            else:
                await ctx.send(_("Game cleared."))