    async def _is_alone(self, ctx: commands.Context):
        channel_members = rgetattr(ctx, "guild.me.voice.channel.members", [])
        nonbots = sum(m.id != ctx.author.id for m in channel_members if not m.bot)
        return nonbots < 1