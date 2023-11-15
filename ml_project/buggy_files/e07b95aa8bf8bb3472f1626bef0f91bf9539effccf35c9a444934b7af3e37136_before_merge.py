    def from_incomplete(cls, *, state, data):
        guild_id = int(data['guild']['id'])
        channel_id = int(data['channel']['id'])
        guild = state._get_guild(guild_id)
        if guild is not None:
            channel = guild.get_channel(channel_id)
        else:
            channel_data = data['channel']
            guild_data = data['guild']
            channel_type = try_enum(ChannelType, channel_data['type'])
            channel = PartialInviteChannel(id=channel_id, name=channel_data['name'], type=channel_type)
            guild = PartialInviteGuild(state, guild_data, guild_id)
        data['guild'] = guild
        data['channel'] = channel
        return cls(state=state, data=data)