    def __init__(self, args):
        super(CmdCacheDir, self).__init__(args)
        self.cache_config = CacheConfig(self.config)