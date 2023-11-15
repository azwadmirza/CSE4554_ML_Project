    def _from_data(self, guild):
        # according to Stan, this is always available even if the guild is unavailable
        # I don't have this guarantee when someone updates the guild.
        member_count = guild.get('member_count', None)
        if member_count is not None:
            self._member_count = member_count

        self.name = guild.get('name')
        self.region = try_enum(VoiceRegion, guild.get('region'))
        self.verification_level = try_enum(VerificationLevel, guild.get('verification_level'))
        self.default_notifications = try_enum(NotificationLevel, guild.get('default_message_notifications'))
        self.explicit_content_filter = try_enum(ContentFilter, guild.get('explicit_content_filter', 0))
        self.afk_timeout = guild.get('afk_timeout')
        self.icon = guild.get('icon')
        self.banner = guild.get('banner')
        self.unavailable = guild.get('unavailable', False)
        self.id = int(guild['id'])
        self._roles = {}
        state = self._state # speed up attribute access
        for r in guild.get('roles', []):
            role = Role(guild=self, data=r, state=state)
            self._roles[role.id] = role

        self.mfa_level = guild.get('mfa_level')
        self.emojis = tuple(map(lambda d: state.store_emoji(self, d), guild.get('emojis', [])))
        self.features = guild.get('features', [])
        self.splash = guild.get('splash')
        self._system_channel_id = utils._get_as_snowflake(guild, 'system_channel_id')
        self.description = guild.get('description')
        self.max_presences = guild.get('max_presences')
        self.max_members = guild.get('max_members')
        self.max_video_channel_users = guild.get('max_video_channel_users')
        self.premium_tier = guild.get('premium_tier', 0)
        self.premium_subscription_count = guild.get('premium_subscription_count') or 0
        self._system_channel_flags = guild.get('system_channel_flags', 0)
        self.preferred_locale = guild.get('preferred_locale')
        self.discovery_splash = guild.get('discovery_splash')
        self._rules_channel_id = utils._get_as_snowflake(guild, 'rules_channel_id')
        self._public_updates_channel_id = utils._get_as_snowflake(guild, 'public_updates_channel_id')

        cache_online_members = self._state._member_cache_flags.online
        cache_joined = self._state._member_cache_flags.joined
        self_id = self._state.self_id
        for mdata in guild.get('members', []):
            member = Member(data=mdata, guild=self, state=state)
            if cache_joined or (cache_online_members and member.raw_status != 'offline') or member.id == self_id:
                self._add_member(member)

        self._sync(guild)
        self._large = None if member_count is None else self._member_count >= 250

        self.owner_id = utils._get_as_snowflake(guild, 'owner_id')
        self.afk_channel = self.get_channel(utils._get_as_snowflake(guild, 'afk_channel_id'))

        for obj in guild.get('voice_states', []):
            self._update_voice_state(obj, int(obj['channel_id']))