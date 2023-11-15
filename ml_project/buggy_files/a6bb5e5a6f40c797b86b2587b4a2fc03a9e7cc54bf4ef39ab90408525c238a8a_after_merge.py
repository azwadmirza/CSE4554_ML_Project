    def __init__(
        self,
        bot: Red,
        scope: str,
        author: int,
        playlist_id: int,
        name: str,
        playlist_url: Optional[str] = None,
        tracks: Optional[List[MutableMapping]] = None,
        guild: Union[discord.Guild, int, None] = None,
    ):
        self.bot = bot
        self.guild = guild
        self.scope = standardize_scope(scope)
        self.config_scope = _prepare_config_scope(self.scope, author, guild)
        self.scope_id = self.config_scope[-1]
        self.author = author
        self.author_id = getattr(self.author, "id", self.author)
        self.guild_id = (
            getattr(guild, "id", guild) if self.scope == PlaylistScope.GLOBAL.value else None
        )
        self.id = playlist_id
        self.name = name
        self.url = playlist_url
        self.tracks = tracks or []
        self.tracks_obj = [lavalink.Track(data=track) for track in self.tracks]