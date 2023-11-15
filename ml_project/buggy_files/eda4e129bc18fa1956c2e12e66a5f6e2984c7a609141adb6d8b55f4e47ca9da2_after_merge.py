    def checkpoint(self):
        """
        Checkpoint this download. Returns a deferred that fires when the checkpointing is completed.
        """
        if self._checkpoint_disabled:
            self._logger.warning("Ignoring checkpoint() call as checkpointing is disabled for this download")
            return succeed(None)

        if not self.handle or not self.handle.is_valid():
            # Libtorrent hasn't received or initialized this download yet
            # 1. Check if we have data for this infohash already (don't overwrite it if we do!)
            basename = hexlify(self.tdef.get_infohash()) + '.state'
            filename = os.path.join(self.session.get_downloads_pstate_dir(), basename)
            if not os.path.isfile(filename):
                # 2. If there is no saved data for this infohash, checkpoint it without data so we do not
                #    lose it when we crash or restart before the download becomes known.
                resume_data = {
                    'file-format': "libtorrent resume file",
                    'file-version': 1,
                    'info-hash': self.tdef.get_infohash()
                }
                alert = type('anonymous_alert', (object, ), dict(resume_data=resume_data))
                self.on_save_resume_data_alert(alert)
            return succeed(None)

        return self.save_resume_data()