    def __init__(self, dbid, dispersy_cid, name, description, nr_torrents, nr_favorite, nr_spam, modified):
        self.id = dbid
        self.name = name
        self.description = description or ''
        self.cid = dispersy_cid
        self.modified = modified or -1
        self.nr_torrents = nr_torrents or 0
        self.nr_favorite = nr_favorite or 0
        self.nr_spam = nr_spam or 0