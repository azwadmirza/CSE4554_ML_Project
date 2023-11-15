    def __init__(self, args):
        super(CmdRemoteConfig, self).__init__(args)
        self.config = RemoteConfig(self.config)