    def __init__(self, dbid, dispersy_cid, name, description, nr_torrents, nr_favorite, nr_spam, modified):
        self.id = dbid
        self.name = name
        self.description = description
        self.cid = dispersy_cid
        self.modified = modified
        self.nr_torrents = nr_torrents
        self.nr_favorite = nr_favorite
        self.nr_spam = nr_spam