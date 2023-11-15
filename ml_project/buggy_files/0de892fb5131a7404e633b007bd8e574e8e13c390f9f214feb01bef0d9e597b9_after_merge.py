    def checkpoint(self):
        """
        Checkpoint this download. Returns a deferred that fires when the checkpointing is completed.
        """
        if self._checkpoint_disabled or not self.handle or not self.handle.is_valid():
            self._logger.warning("Ignoring checkpoint() call as checkpointing is disabled for this download "
                                 "or the handle is not ready.")
            return succeed(None)

        return self.save_resume_data()