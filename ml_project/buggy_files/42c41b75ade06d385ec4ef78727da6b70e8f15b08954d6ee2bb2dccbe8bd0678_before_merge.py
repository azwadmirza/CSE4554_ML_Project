    def RescanShares(self, msg, rebuild=False):

        try:
            files, streams, wordindex, fileindex, mtimes = self.rescandirs(
                msg.shared,
                self.config.sections["transfers"]["sharedmtimes"],
                self.config.sections["transfers"]["sharedfiles"],
                self.config.sections["transfers"]["sharedfilesstreams"],
                msg.yieldfunction,
                self.np.frame.SharesProgress,
                name=_("Shares"),
                rebuild=rebuild
            )

            time.sleep(0.5)

            self.np.frame.RescanFinished(
                files, streams, wordindex, fileindex, mtimes,
                "normal"
            )
        except Exception as ex:
            config_dir, data_dir = GetUserDirectories()
            log.addwarning(
                _("Failed to rebuild share, serious error occurred. If this problem persists delete %s/*.db and try again. If that doesn't help please file a bug report with the stack trace included (see terminal output after this message). Technical details: %s") % (data_dir, ex)
            )
            raise