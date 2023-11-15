    async def _get_announce_channel(self, guild: discord.Guild) -> discord.TextChannel:
        channel_id = await self.config.guild(guild).announce_channel()
        channel = None

        if channel_id is not None:
            channel = guild.get_channel(channel_id)

        if channel is None:
            channel = guild.default_channel

        return channel