    def __init__(self, infohash, name, length, num_files, category_list, creation_date, seeders, leechers, cid):
        self.infohash = infohash
        self.name = name
        self.length = length or 0
        self.num_files = num_files or 0
        self.category_list = category_list or []
        self.creation_date = creation_date or -1
        self.seeders = seeders or 0
        self.leechers = leechers or 0
        self.cid = cid