    def checkpoint(self):
        """ Called by any thread """
        if self._checkpoint_disabled:
            self._logger.warning("Ignoring checkpoint() call as is checkpointing disabled for this download.")
        else:
            infohash, pstate = self.network_checkpoint()
            checkpoint = lambda: self.session.lm.save_download_pstate(infohash, pstate)
            self.session.lm.threadpool.add_task(checkpoint, 0)