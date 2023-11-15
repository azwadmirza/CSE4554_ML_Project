    def parse_guild_member_add(self, data):
        guild = self._get_guild(int(data['guild_id']))
        if guild is None:
            log.debug('GUILD_MEMBER_ADD referencing an unknown guild ID: %s. Discarding.', data['guild_id'])
            return

        member = Member(guild=guild, data=data, state=self)
        if self._member_cache_flags.joined:
            guild._add_member(member)

        try:
            guild._member_count += 1
        except AttributeError:
            pass

        self.dispatch('member_join', member)