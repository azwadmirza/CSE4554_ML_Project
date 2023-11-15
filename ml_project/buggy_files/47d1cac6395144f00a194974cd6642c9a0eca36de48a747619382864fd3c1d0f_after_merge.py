    def parse_presence_update(self, data):
        guild_id = utils._get_as_snowflake(data, 'guild_id')
        guild = self._get_guild(guild_id)
        if guild is None:
            log.debug('PRESENCE_UPDATE referencing an unknown guild ID: %s. Discarding.', guild_id)
            return

        user = data['user']
        member_id = int(user['id'])
        member = guild.get_member(member_id)
        flags = self.member_cache_flags
        if member is None:
            if 'username' not in user:
                # sometimes we receive 'incomplete' member data post-removal.
                # skip these useless cases.
                return

            member, old_member = Member._from_presence_update(guild=guild, data=data, state=self)
            if flags.online or (flags._online_only and member.raw_status != 'offline'):
                guild._add_member(member)
        else:
            old_member = Member._copy(member)
            user_update = member._presence_update(data=data, user=user)
            if user_update:
                self.dispatch('user_update', user_update[0], user_update[1])

            if member.id != self.self_id and flags._online_only and member.raw_status == 'offline':
                guild._remove_member(member)

        self.dispatch('member_update', old_member, member)