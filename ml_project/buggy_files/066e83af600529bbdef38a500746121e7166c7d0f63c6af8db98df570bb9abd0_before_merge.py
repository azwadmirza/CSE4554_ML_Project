    def pm_check(self, ctx):
        return isinstance(ctx.channel, discord.DMChannel)