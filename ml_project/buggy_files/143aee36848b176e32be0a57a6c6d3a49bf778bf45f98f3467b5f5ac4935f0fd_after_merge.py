    def __init__(self, bot: Red, session: aiohttp.ClientSession):
        self.bot = bot
        self.session = session
        self.spotify_token: Optional[MutableMapping[str, Union[str, int]]] = None
        self.client_id = None
        self.client_secret = None