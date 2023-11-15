    def feed_all(self, masterid):
        for scanid in self.get_scans():
            self.feed(masterid, scanid)