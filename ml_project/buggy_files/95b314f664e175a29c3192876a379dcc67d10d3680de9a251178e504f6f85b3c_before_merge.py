def setup(bot: commands.Bot):
    cog = Audio(bot)
    bot.add_cog(cog)