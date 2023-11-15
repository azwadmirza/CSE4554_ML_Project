    def __init__(self, repo, config):
        super(RemoteHTTP, self).__init__(repo, config)
        self.cache_dir = config.get(Config.SECTION_REMOTE_URL)
        self.url = self.cache_dir

        self.path_info = HTTPPathInfo()