    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, 2711759130, force_registration=True)
        self.skip_votes = {}
        self.session = aiohttp.ClientSession()
        self._connect_task = None
        self._disconnect_task = None
        self._cleaned_up = False
        self._connection_aborted = False
        self.play_lock = {}
        self._manager: Optional[ServerManager] = None
        self._cog_name = None
        self._cog_id = None
        default_global = dict(
            schema_version=1,
            cache_level=0,
            cache_age=365,
            status=False,
            use_external_lavalink=False,
            restrict=True,
            current_version=redbot.core.VersionInfo.from_str("3.0.0a0").to_json(),
            localpath=str(cog_data_path(raw_name="Audio")),
            **self._default_lavalink_settings,
        )

        default_guild = dict(
            auto_play=False,
            autoplaylist=dict(enabled=False, id=None, name=None, scope=None),
            disconnect=False,
            dj_enabled=False,
            dj_role=None,
            emptydc_enabled=False,
            emptydc_timer=0,
            emptypause_enabled=False,
            emptypause_timer=0,
            jukebox=False,
            jukebox_price=0,
            maxlength=0,
            notify=False,
            repeat=False,
            shuffle=False,
            thumbnail=False,
            volume=100,
            vote_enabled=False,
            vote_percent=0,
            room_lock=None,
            url_keyword_blacklist=[],
            url_keyword_whitelist=[],
        )
        _playlist = dict(id=None, author=None, name=None, playlist_url=None, tracks=[])
        self.config.init_custom("EQUALIZER", 1)
        self.config.register_custom("EQUALIZER", eq_bands=[], eq_presets={})
        self.config.init_custom(PlaylistScope.GLOBAL.value, 1)
        self.config.register_custom(PlaylistScope.GLOBAL.value, **_playlist)
        self.config.init_custom(PlaylistScope.GUILD.value, 2)
        self.config.register_custom(PlaylistScope.GUILD.value, **_playlist)
        self.config.init_custom(PlaylistScope.USER.value, 2)
        self.config.register_custom(PlaylistScope.USER.value, **_playlist)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)
        self.music_cache = MusicCache(bot, self.session, path=str(cog_data_path(raw_name="Audio")))
        self.play_lock = {}

        self._manager: Optional[ServerManager] = None
        # These has to be a task since this requires the bot to be ready
        # If it waits for ready in startup, we cause a deadlock during initial load
        # as initial load happens before the bot can ever be ready.
        self._init_task = self.bot.loop.create_task(self.initialize())
        self._ready_event = asyncio.Event()