    def __init__(self, session, cid, infohash):
        BaseChannelsEndpoint.__init__(self, session)
        self.cid = cid
        self.infohash = infohash