    def startFactory(self):
        # start the pool thread with default configs
        self.pool_service = PoolService()
        self.pool_service.start_pool()