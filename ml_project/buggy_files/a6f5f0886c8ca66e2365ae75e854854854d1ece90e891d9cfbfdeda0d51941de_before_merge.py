    def __init__(self, bot: Red, session: aiohttp.ClientSession, path: str):
        self.bot = bot
        self.spotify_api: SpotifyAPI = SpotifyAPI(bot, session)
        self.youtube_api: YouTubeAPI = YouTubeAPI(bot, session)
        self._session: aiohttp.ClientSession = session
        if HAS_SQL:
            self.database: Database = Database(
                f'sqlite:///{os.path.abspath(str(os.path.join(path, "cache.db")))}'
            )
        else:
            self.database = None

        self._tasks: dict = {}
        self._lock: asyncio.Lock = asyncio.Lock()
        self.config: Optional[Config] = None