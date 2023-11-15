    def __init__(self, session):
        BaseMyChannelEndpoint.__init__(self, session)
        self.putChild(b"torrents", MyChannelTorrentsEndpoint(session))
        self.putChild(b"commit", MyChannelCommitEndpoint(session))