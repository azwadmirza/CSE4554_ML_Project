    def RescanBuddyShares(self, msg, rebuild=False):

        files, streams, wordindex, fileindex, mtimes = self.rescandirs(
            msg.shared,
            self.config.sections["transfers"]["bsharedmtimes"],
            self.config.sections["transfers"]["bsharedfiles"],
            self.config.sections["transfers"]["bsharedfilesstreams"],
            msg.yieldfunction,
            self.np.frame.BuddySharesProgress,
            name=_("Buddy Shares"),
            rebuild=rebuild
        )

        time.sleep(0.5)

        self.np.frame.RescanFinished(
            files, streams, wordindex, fileindex, mtimes,
            "buddy"
        )