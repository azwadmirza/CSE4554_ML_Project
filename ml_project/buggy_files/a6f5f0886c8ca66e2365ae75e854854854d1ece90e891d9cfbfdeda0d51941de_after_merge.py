    def __init__(self, bot: Red, session: aiohttp.ClientSession):
        self.bot = bot
        self.spotify_api: SpotifyAPI = SpotifyAPI(bot, session)
        self.youtube_api: YouTubeAPI = YouTubeAPI(bot, session)
        self._session: aiohttp.ClientSession = session
        self.database = _database

        self._tasks: MutableMapping = {}
        self._lock: asyncio.Lock = asyncio.Lock()
        self.config: Optional[Config] = None