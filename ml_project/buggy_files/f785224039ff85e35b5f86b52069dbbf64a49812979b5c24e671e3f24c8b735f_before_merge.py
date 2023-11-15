    def __init__(self, session, infohash):
        DownloadBaseEndpoint.__init__(self, session)
        self.infohash = bytes(infohash.decode('hex'))
        self.putChild("torrent", DownloadExportTorrentEndpoint(session, self.infohash))