    def __init__(self, *, dispatch, handlers, hooks, syncer, http, loop, **options):
        self.loop = loop
        self.http = http
        self.max_messages = options.get('max_messages', 1000)
        if self.max_messages is not None and self.max_messages <= 0:
            self.max_messages = 1000

        self.dispatch = dispatch
        self.syncer = syncer
        self.is_bot = None
        self.handlers = handlers
        self.hooks = hooks
        self.shard_count = None
        self._ready_task = None
        self.heartbeat_timeout = options.get('heartbeat_timeout', 60.0)
        self.guild_ready_timeout = options.get('guild_ready_timeout', 2.0)
        if self.guild_ready_timeout < 0:
            raise ValueError('guild_ready_timeout cannot be negative')

        self.guild_subscriptions = options.get('guild_subscriptions', True)
        allowed_mentions = options.get('allowed_mentions')

        if allowed_mentions is not None and not isinstance(allowed_mentions, AllowedMentions):
            raise TypeError('allowed_mentions parameter must be AllowedMentions')

        self.allowed_mentions = allowed_mentions
        self._chunk_requests = {} # Dict[Union[int, str], ChunkRequest]

        activity = options.get('activity', None)
        if activity:
            if not isinstance(activity, BaseActivity):
                raise TypeError('activity parameter must derive from BaseActivity.')

            activity = activity.to_dict()

        status = options.get('status', None)
        if status:
            if status is Status.offline:
                status = 'invisible'
            else:
                status = str(status)

        intents = options.get('intents', None)
        if intents is not None:
            if not isinstance(intents, Intents):
                raise TypeError('intents parameter must be Intent not %r' % type(intents))
        else:
            intents = Intents.default()

        if not intents.guilds:
            log.warning('Guilds intent seems to be disabled. This may cause state related issues.')

        try:
            chunk_guilds = options['fetch_offline_members']
        except KeyError:
            chunk_guilds = options.get('chunk_guilds_at_startup', intents.members)
        else:
            msg = 'fetch_offline_members is deprecated, use chunk_guilds_at_startup instead'
            warnings.warn(msg, DeprecationWarning, stacklevel=4)

        self._chunk_guilds = chunk_guilds

        # Ensure these two are set properly
        if not intents.members and self._chunk_guilds:
            raise ValueError('Intents.members must be enabled to chunk guilds at startup.')

        cache_flags = options.get('member_cache_flags', None)
        if cache_flags is None:
            cache_flags = MemberCacheFlags.from_intents(intents)
        else:
            if not isinstance(cache_flags, MemberCacheFlags):
                raise TypeError('member_cache_flags parameter must be MemberCacheFlags not %r' % type(cache_flags))

            cache_flags._verify_intents(intents)

        self._member_cache_flags = cache_flags
        self._activity = activity
        self._status = status
        self._intents = intents

        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith('parse_'):
                parsers[attr[6:].upper()] = func

        self.clear()