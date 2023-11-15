    def checkpoint(self):
        """
        Checkpoint this download. Returns a deferred that fires when the checkpointing is completed.
        """
        if self._checkpoint_disabled:
            self._logger.warning("Ignoring checkpoint() call as checkpointing is disabled for this download")
            return succeed(None)

        if not self.handle or not self.handle.is_valid():
            resume_data = {
                'file-format': "libtorrent resume file",
                'file-version': 1,
                'info-hash': self.tdef.get_infohash()
            }
            alert = type('anonymous_alert', (object, ), dict(resume_data=resume_data))
            self.on_save_resume_data_alert(alert)
            return succeed(None)

        return self.save_resume_data()