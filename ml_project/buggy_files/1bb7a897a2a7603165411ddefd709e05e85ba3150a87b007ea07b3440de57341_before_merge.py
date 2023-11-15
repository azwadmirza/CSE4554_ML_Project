    def guiservthread_checkpoint_timer(self):
        """ Periodically checkpoint Session """
        if self.done:
            return
        try:
            self._logger.info("main: Checkpointing Session")
            self.utility.session.checkpoint()

            self.utility.session.lm.threadpool.call_in_thread(SESSION_CHECKPOINT_INTERVAL, self.guiservthread_checkpoint_timer)
        except:
            print_exc()