    def __init__(self, bot):
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, 2711759130, force_registration=True)
        self.skip_votes: MutableMapping[discord.Guild, List[discord.Member]] = {}
        self.play_lock: MutableMapping[int, bool] = {}
        self._dj_status_cache: MutableMapping[int, Optional[bool]] = {}
        self._dj_role_cache: MutableMapping[int, Optional[int]] = {}
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._connect_task: Optional[asyncio.Task] = None
        self._disconnect_task: Optional[asyncio.Task] = None
        self._cleaned_up: bool = False
        self._connection_aborted: bool = False
        self._manager: Optional[ServerManager] = None
        default_global: Mapping = dict(
            schema_version=1,
            cache_level=0,
            cache_age=365,
            status=False,
            use_external_lavalink=False,
            restrict=True,
            localpath=str(cog_data_path(raw_name="Audio")),
            url_keyword_blacklist=[],
            url_keyword_whitelist=[],
            **self._default_lavalink_settings,
        )

        default_guild: Mapping = dict(
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
            shuffle_bumped=True,
            thumbnail=False,
            volume=100,
            vote_enabled=False,
            vote_percent=0,
            room_lock=None,
            url_keyword_blacklist=[],
            url_keyword_whitelist=[],
        )
        _playlist: Mapping = dict(id=None, author=None, name=None, playlist_url=None, tracks=[])
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
        self.music_cache: Optional[MusicCache] = None
        self._error_counter: Counter = Counter()
        self._error_timer: MutableMapping[int, int] = {}
        self._disconnected_players: MutableMapping[int, bool] = {}

        # These has to be a task since this requires the bot to be ready
        # If it waits for ready in startup, we cause a deadlock during initial load
        # as initial load happens before the bot can ever be ready.
        self._init_task: asyncio.Task = self.bot.loop.create_task(self.initialize())
        self._ready_event: asyncio.Event = asyncio.Event()