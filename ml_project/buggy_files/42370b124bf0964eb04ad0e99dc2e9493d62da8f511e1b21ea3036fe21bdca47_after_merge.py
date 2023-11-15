    def __init__(self, args):
        super(CmdRemoteConfig, self).__init__(args)
        self.remote_config = RemoteConfig(self.config)