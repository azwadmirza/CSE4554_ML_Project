    def guiservthread_checkpoint_timer(self):
        """ Periodically checkpoint Session """
        self._logger.info("main: Checkpointing Session")
        return deferToThread(self.utility.session.checkpoint)