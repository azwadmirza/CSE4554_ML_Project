    def __init__(self, profile_name, target_name, config, threads,
                 credentials):
        self.profile_name = profile_name
        self.target_name = target_name
        if isinstance(config, dict):
            config = UserConfig.from_dict(config)
        self.config = config
        self.threads = threads
        self.credentials = credentials