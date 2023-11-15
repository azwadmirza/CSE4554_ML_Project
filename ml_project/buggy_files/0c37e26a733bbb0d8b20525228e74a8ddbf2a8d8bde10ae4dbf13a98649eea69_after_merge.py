    def actionJumpStart_trigger(self, checked=True):
        log.debug("actionJumpStart_trigger")

        # Seek to the 1st frame
        self.SeekSignal.emit(1)