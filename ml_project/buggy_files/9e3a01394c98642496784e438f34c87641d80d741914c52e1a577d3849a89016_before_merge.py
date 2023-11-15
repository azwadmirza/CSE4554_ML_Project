    async def announce_channel(self, ctx, channel: discord.TextChannel=None):
        """
        Changes the channel on which the bot makes announcements.
        """
        if channel is None:
            channel = ctx.channel
        await self.conf.guild(ctx.guild).set("announce_channel", channel.id)

        await ctx.send("The announcement channel has been set to {}".format(
            channel.mention
        ))