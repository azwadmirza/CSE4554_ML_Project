    def from_incomplete(cls, *, state, data):
        try:
            guild_id = int(data['guild']['id'])
        except KeyError:
            # If we're here, then this is a group DM
            guild = None
        else:
            guild = state._get_guild(guild_id)
            if guild is None:
                # If it's not cached, then it has to be a partial guild
                guild_data = data['guild']
                guild = PartialInviteGuild(state, guild_data, guild_id)

        # As far as I know, invites always need a channel
        # So this should never raise.
        channel_data = data['channel']
        channel_id = int(channel_data['id'])
        channel_type = try_enum(ChannelType, channel_data['type'])
        channel = PartialInviteChannel(id=channel_id, name=channel_data['name'], type=channel_type)
        if guild is not None:
            # Upgrade the partial data if applicable
            channel = guild.get_channel(channel_id) or channel

        data['guild'] = guild
        data['channel'] = channel
        return cls(state=state, data=data)