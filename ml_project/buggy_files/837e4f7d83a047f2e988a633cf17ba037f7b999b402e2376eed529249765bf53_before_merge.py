    async def initialize(self, config: Config):
        if HAS_SQL:
            await self.database.connect()

            await self.database.execute(query="PRAGMA temp_store = 2;")
            await self.database.execute(query="PRAGMA journal_mode = wal;")
            await self.database.execute(query="PRAGMA wal_autocheckpoint;")
            await self.database.execute(query="PRAGMA read_uncommitted = 1;")

            await self.database.execute(query=_CREATE_LAVALINK_TABLE)
            await self.database.execute(query=_CREATE_UNIQUE_INDEX_LAVALINK_TABLE)
            await self.database.execute(query=_CREATE_YOUTUBE_TABLE)
            await self.database.execute(query=_CREATE_UNIQUE_INDEX_YOUTUBE_TABLE)
            await self.database.execute(query=_CREATE_SPOTIFY_TABLE)
            await self.database.execute(query=_CREATE_UNIQUE_INDEX_SPOTIFY_TABLE)
        self.config = config