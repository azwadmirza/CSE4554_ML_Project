    def __init__(self, args):
        super(CmdCacheDir, self).__init__(args)
        self.config = CacheConfig(self.config)