    def RebuildBuddyShares(self, msg):
        self._RescanShares(msg, "buddy", rebuild=True)