    def __init__(self, session, cid, path):
        BaseChannelsEndpoint.__init__(self, session)
        self.cid = cid
        self.path = path
        self.deferred = Deferred()