    def _RescanFinished(self, files, streams, wordindex, fileindex, mtimes):

        self.np.config.setShares(files, streams, wordindex, fileindex, mtimes)

        if self.np.config.sections["transfers"]["shared"]:
            self.rescan_public.set_sensitive(True)
            self.browse_public_shares.set_sensitive(True)

        self.rescanning = 0
        self.logMessage(_("Rescanning finished"))

        self.SharesProgress.hide()

        self.np.shares.CompressShares("normal")

        if self.np.transfers is not None:
            self.np.shares.sendNumSharedFoldersFiles()