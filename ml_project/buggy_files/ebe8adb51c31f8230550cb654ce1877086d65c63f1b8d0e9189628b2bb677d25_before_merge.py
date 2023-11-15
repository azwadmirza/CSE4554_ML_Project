    def __init__(self, max_wait_time):
        self.mtime = dict()
        self.exists_local = ExistsDict(self)
        self.exists_remote = ExistsDict(self)
        self.size = dict()
        # Indicator whether an inventory has been created for the root of a given IOFile.
        # In case of remote objects the root is the bucket or server host.
        self.has_inventory = set()
        self.active = True
        self.remaining_wait_time = max_wait_time
        self.max_wait_time = max_wait_time