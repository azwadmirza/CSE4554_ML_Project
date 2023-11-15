    async def initialize(self, config: Config):
        self.config = config
        await _database.init()