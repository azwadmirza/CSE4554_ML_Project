    def __init__(self, session):
        super(GigaChannelManager, self).__init__()
        self.session = session
        self.channels_lc = None