    def _BuddyRescanFinished(self, files, streams, wordindex, fileindex, mtimes):

        self.np.config.setBuddyShares(files, streams, wordindex, fileindex, mtimes)
        self.np.config.writeShares()

        if self.np.config.sections["transfers"]["enablebuddyshares"]:
            self.rescan_buddy.set_sensitive(True)
            self.browse_buddy_shares.set_sensitive(True)

        if self.np.transfers is not None:
            self.np.shares.sendNumSharedFoldersFiles()

        self.brescanning = 0
        self.logMessage(_("Rescanning Buddy Shares finished"))

        self.BuddySharesProgress.hide()
        self.np.shares.CompressShares("buddy")